import os
import torch
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModel, XLMRobertaTokenizerFast, XLMRobertaForSequenceClassification

# ── SBERT ─────────────────────────────────────────────────────────────────────

_sbert_model = None


def get_sbert() -> SentenceTransformer:
    global _sbert_model
    if _sbert_model is None:
        _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _sbert_model


# ── Emotion pipeline ──────────────────────────────────────────────────────────

_emotion_pipeline = None


def get_emotion_pipeline():
    global _emotion_pipeline
    if _emotion_pipeline is None:
        _emotion_pipeline = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
        )
    return _emotion_pipeline


# ── Nemotron (nvidia/llama-embed-nemotron-8b) ─────────────────────────────────

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
            _nemotron_tokenizer = AutoTokenizer.from_pretrained(
                _NEMOTRON_MODEL_NAME,
                trust_remote_code=True,
                padding_side="left",         # as in the notebook
            )

            _nemotron_model = AutoModel.from_pretrained(
                _NEMOTRON_MODEL_NAME,
                trust_remote_code=True,
                dtype=torch.float32,         # as in the notebook
            )

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            _nemotron_model.to(device)
            _nemotron_model.eval()

        except Exception as exc:
            # Reset so the next call retries
            _nemotron_tokenizer = None
            _nemotron_model     = None
            raise RuntimeError(f"Failed to load Nemotron model: {exc}") from exc

    return _nemotron_tokenizer, _nemotron_model

# ── Tone ─────────────────────────────────
_FORMALITY_MODEL_NAME = "s-nlp/xlmr_formality_classifier"
 
_formality_tokenizer = None
_formality_model     = None
_id2formality        = {0: "formal", 1: "informal"}
 
 
def get_formality_model():
    """
    Returns (tokenizer, model, id2formality) for the XLM-RoBERTa formality
    classifier.  Model is lazy-loaded and cached on first call.
 
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
            _formality_model.eval()
        except Exception as exc:
            _formality_tokenizer = None
            _formality_model     = None
            raise RuntimeError(f"Failed to load formality model: {exc}") from exc
 
    return _formality_tokenizer, _formality_model, _id2formality