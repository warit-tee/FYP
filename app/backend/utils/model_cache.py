import ast
import os

import pandas as pd
import torch
import warnings
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModel,
    XLMRobertaTokenizerFast,
    XLMRobertaForSequenceClassification,
)

from openai import AzureOpenAI  # optional dependency
from dotenv import load_dotenv


# ── SBERT ─────────────────────────────────────────────────────────────────────

_sbert_model = None


def _get_torch_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def has_gpu() -> bool:
    return _get_torch_device() == "cuda"


def get_sbert() -> SentenceTransformer:
    global _sbert_model
    if _sbert_model is None:
        _sbert_model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device=_get_torch_device(),
        )
    return _sbert_model


# ── Emotion pipeline ──────────────────────────────────────────────────────────

_emotion_pipeline = None


def get_emotion_pipeline():
    global _emotion_pipeline
    if _emotion_pipeline is None:
        pipeline_device = 0 if has_gpu() else -1
        _emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
            device=pipeline_device,
        )
    return _emotion_pipeline


# ── Nemotron (nvidia/llama-embed-nemotron-8b) ───────────────────────────────

_NEMOTRON_MODEL_NAME = "nvidia/llama-embed-nemotron-8b"

_nemotron_tokenizer = None
_nemotron_model     = None


def get_nemotron_model():
    """
    Returns (tokenizer, model) for nvidia/llama-embed-nemotron-8b.

    Loading strategy (mirrors llama_nemotron_8b.ipynb):
      - padding_side = "left"  (required by the model)
      - dtype = torch.float32
      - Move to CUDA if available, else CPU
      - Set eval() mode

    Raises RuntimeError if the model cannot be loaded (e.g. not enough VRAM/RAM).
    """
    global _nemotron_tokenizer, _nemotron_model

    if _nemotron_tokenizer is None or _nemotron_model is None:
        try:
            if not has_gpu():
                raise RuntimeError(
                    "Nemotron is disabled on CPU-only environments due to model size"
                )

            device = _get_torch_device()
            model_dtype = torch.float16 if device == "cuda" else torch.float32

            _nemotron_tokenizer = AutoTokenizer.from_pretrained(
                _NEMOTRON_MODEL_NAME,
                trust_remote_code=True,
                padding_side="left",
            )
            _nemotron_model = AutoModel.from_pretrained(
                _NEMOTRON_MODEL_NAME,
                trust_remote_code=True,
                torch_dtype=model_dtype,
            )
            _nemotron_model.to(device)
            _nemotron_model.eval()

        except Exception as exc:
            _nemotron_tokenizer = None
            _nemotron_model     = None
            raise RuntimeError(f"Failed to load Nemotron model: {exc}") from exc

    return _nemotron_tokenizer, _nemotron_model


# ── Formality classifier ──────────────────────────────────────────────────────

_FORMALITY_MODEL_NAME = "s-nlp/xlmr_formality_classifier"

_formality_tokenizer = None
_formality_model     = None
_id2formality        = {0: "formal", 1: "informal"}


def get_formality_model():
    """
    Returns (tokenizer, model, id2formality) for the XLM-RoBERTa formality
    classifier. Model is lazy-loaded and cached on first call.

    Raises RuntimeError if loading fails.
    """
    global _formality_tokenizer, _formality_model

    if _formality_tokenizer is None or _formality_model is None:
        try:
            _formality_tokenizer = XLMRobertaTokenizerFast.from_pretrained(
                _FORMALITY_MODEL_NAME
            )
            _formality_model = XLMRobertaForSequenceClassification.from_pretrained(
                _FORMALITY_MODEL_NAME
            )
            _formality_model.to(_get_torch_device())
            _formality_model.eval()
        except Exception as exc:
            _formality_tokenizer = None
            _formality_model     = None
            raise RuntimeError(f"Failed to load formality model: {exc}") from exc

    return _formality_tokenizer, _formality_model, _id2formality


# ── TF-IDF corpus vectorizer ──────────────────────────────────────────────────

_CORPUS_PATH = os.path.join(
    os.path.dirname(__file__),      # utils/
    "dataset", "preprocessed_corpus.csv",
)

_tfidf_vectorizer: TfidfVectorizer | None = None


def get_tfidf_vectorizer() -> TfidfVectorizer | None:
    """
    Returns a TfidfVectorizer already fitted on the preprocessed corpus.

    The CSV's 'Stemming' column contains Python list literals of stemmed tokens
    (e.g. "['integr', 'social', ...]"). Each row is joined into a space-separated
    string before fitting, matching the output of similarity._preprocess().

    Returns None (with a warning) if the corpus file is missing, allowing
    similarity.tfidf_similarity() to fall back to fitting on the input pair.
    """
    global _tfidf_vectorizer

    if _tfidf_vectorizer is not None:
        return _tfidf_vectorizer

    corpus_path = os.path.normpath(_CORPUS_PATH)

    try:
        df = pd.read_csv(corpus_path, engine="python", on_bad_lines="skip")
    except FileNotFoundError:
        warnings.warn(
            f"TF-IDF corpus not found at {corpus_path}. "
            "Falling back to per-query vectorizer fitting.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    if "Stemming" not in df.columns:
        raise ValueError(
            f"'Stemming' column not found in corpus CSV. "
            f"Available columns: {df.columns.tolist()}"
        )

    corpus_docs: list[str] = []
    for raw in df["Stemming"].dropna():
        raw = str(raw).strip()
        if raw.startswith("["):
            try:
                tokens = ast.literal_eval(raw)
                corpus_docs.append(" ".join(str(t) for t in tokens))
                continue
            except (ValueError, SyntaxError):
                pass
        corpus_docs.append(raw)

    if not corpus_docs:
        raise ValueError("Corpus CSV contained no usable rows in 'Stemming' column.")

    vec = TfidfVectorizer(ngram_range=(1, 1))
    vec.fit(corpus_docs)
    _tfidf_vectorizer = vec
    return _tfidf_vectorizer


# ── Azure OpenAI client (for factual consistency service) ─────────────────────

_openai_client = None


def get_openai_client():
    """
    Returns a lazy-loaded AzureOpenAI client configured from environment
    variables:

      OPENAI_API_KEY          – Azure OpenAI API key
      OPENAI_API_ENDPOINT     – Azure OpenAI endpoint URL
      OPENAI_API_VERSION      – API version string (e.g. "2024-12-01-preview")

    Returns None (with a warning) if any required variable is missing, so
    callers can gracefully degrade instead of crashing.
    """
    load_dotenv()
    global _openai_client

    if _openai_client is not None:
        return _openai_client

    api_key      = os.getenv("OPENAI_API_KEY")
    api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
    api_version  = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")

    if not api_key or not api_endpoint:
        warnings.warn(
            "OPENAI_API_KEY or OPENAI_API_ENDPOINT not set. "
            "Factual consistency analysis will be unavailable.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    try:
        _openai_client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=api_endpoint,
            api_version=api_version,
        )
    except Exception as exc:
        warnings.warn(
            f"Failed to initialise AzureOpenAI client: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return None

    print("Azure OpenAI client initialized successfully.")
    return _openai_client


def get_openai_deployment() -> str:
    """
    Returns the Azure OpenAI deployment name from the environment variable
    OPENAI_DEPLOYMENT_NAME (defaults to "gpt-4o-mini").
    """
    return os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-5-mini")