import re

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from utils.model_cache import get_sbert, get_nemotron_model, get_tfidf_vectorizer

# ── One-time NLTK downloads ─────────────────────────────────────────────────
for _pkg in ("punkt", "punkt_tab", "stopwords"):
    try:
        nltk.download(_pkg, quiet=True)
    except Exception:
        pass


# ── Preprocessing (mirrors TF-IDF.ipynb) ────────────────────────────────────

_STOPWORDS = set(stopwords.words("english"))
_STEMMER   = PorterStemmer()


def _preprocess(text: str) -> str:
    """
    Apply the same pipeline used in TF-IDF.ipynb:
      lowercase → remove punctuation → strip → tokenize
      → remove stopwords → stem → join with spaces
    Returns a single string ready for TfidfVectorizer.
    """
    text   = text.lower()
    text   = re.sub(r"[^\w\s]", "", text)
    text   = text.strip()
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in _STOPWORDS]
    tokens = [_STEMMER.stem(t) for t in tokens]
    return " ".join(tokens)


# ── TF-IDF similarity ────────────────────────────────────────────────────────

def tfidf_similarity(text1: str, text2: str) -> float:
    """
    Pre-process both texts exactly as in TF-IDF.ipynb, then compute cosine
    similarity between their TF-IDF vectors.

    IDF weights are derived from the preprocessed corpus (fitted once at
    startup). If the corpus CSV is unavailable, the vectorizer falls back to
    fitting on the two input texts only (original behaviour).
    """
    p1 = _preprocess(text1)
    p2 = _preprocess(text2)

    vec = get_tfidf_vectorizer()

    if vec is None:
        # Corpus not available — fit on the pair (fallback)
        vec = TfidfVectorizer(ngram_range=(1, 1))
        tfidf = vec.fit_transform([p1, p2])
    else:
        # Transform using corpus-derived IDF weights
        tfidf = vec.transform([p1, p2])

    sim = cosine_similarity(tfidf[0], tfidf[1])[0][0]
    return float(sim)


# ── SBERT similarity ─────────────────────────────────────────────────────────

def sbert_similarity(text1: str, text2: str) -> float:
    model      = get_sbert()
    emb1, emb2 = model.encode([text1, text2])
    sim        = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return float(sim)


# ── Nemotron (local HuggingFace, mirrors llama_nemotron_8b.ipynb) ────────────

_STS_INSTRUCTION = "Retrieve semantically similar text."


def _get_nemotron_embedding(text: str) -> np.ndarray:
    """
    Compute a single embedding using the local Nemotron model.
    Follows the exact procedure in llama_nemotron_8b.ipynb:
      - Prepend instruction
      - Tokenise with left-padding, max_length=8192
      - Mean-pool over non-padded tokens
      - L2-normalise
    """
    tokenizer, model = get_nemotron_model()
    device = next(model.parameters()).device

    input_text = f"Instruct: {_STS_INSTRUCTION}\nQuery: {text}"

    inputs = tokenizer(
        input_text,
        max_length=8192,
        padding=True,
        truncation=True,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():
        output = model(**inputs)

    token_embeddings = output.last_hidden_state          # (1, seq_len, hidden)
    attention_mask   = inputs["attention_mask"]          # (1, seq_len)

    mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_emb  = torch.sum(token_embeddings * mask_expanded, dim=1)
    sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
    mean_emb = sum_emb / sum_mask                        # (1, hidden)

    normalised = F.normalize(mean_emb, p=2, dim=1)      # L2 norm
    return normalised[0].cpu().numpy()


def nemotron_similarity(text1: str, text2: str) -> tuple[float | None, str | None]:
    """
    Returns (similarity_score, error_message).
    error_message is None on success; score is None on failure.
    """
    try:
        emb1 = _get_nemotron_embedding(text1)
        emb2 = _get_nemotron_embedding(text2)
        sim  = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(sim), None
    except Exception as exc:
        return None, str(exc)


# ── Combined entry point ─────────────────────────────────────────────────────

def all_methods(text1: str, text2: str) -> dict:
    tfidf        = tfidf_similarity(text1, text2)
    sbert        = sbert_similarity(text1, text2)
    nem, nem_err = nemotron_similarity(text1, text2)

    result = {
        "similarity": {
            "tfidf":    round(tfidf, 6),
            "sbert":    round(sbert, 6),
            "nemotron": round(nem, 6) if nem is not None else None,
        },
        "difference": {
            "tfidf":    round(1 - tfidf, 6),
            "sbert":    round(1 - sbert, 6),
            "nemotron": round(1 - nem,   6) if nem is not None else None,
        },
    }
    if nem_err:
        result["nemotron_error"] = nem_err
    return result