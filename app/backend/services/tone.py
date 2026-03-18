import re
import numpy as np
from utils.model_cache import get_formality_model


# ── Sentence splitting (mirrors tone.py notebook) ────────────────────────────

def _split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences on sentence-ending punctuation followed by
    an uppercase letter (or opening bracket/quote), exactly as in the notebook.
    """
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\(\[])', text)
    return [s.strip() for s in sentences if s.strip()]


# ── Sentence-level formality scoring ────────────────────────────────────────

def _get_formality_scores(sentences: list[str]) -> list[dict]:
    """
    Run the XLM-RoBERTa formality classifier over a list of sentences.

    Returns a list of dicts, one per sentence:
        {"formal": float, "informal": float}   (softmax probabilities)
    """
    tokenizer, model, id2formality = get_formality_model()

    encoding = tokenizer(
        sentences,
        add_special_tokens=True,
        return_token_type_ids=True,
        truncation=True,
        padding="max_length",
        return_tensors="pt",
    )

    import torch
    with torch.no_grad():
        output = model(**encoding)

    formality_scores = [
        {id2formality[idx]: score for idx, score in enumerate(text_scores.tolist())}
        for text_scores in output.logits.softmax(dim=1)
    ]
    return formality_scores


# ── Essay-level aggregation ──────────────────────────────────────────────────

def _get_mean_formality_scores(formality_scores: list[dict]) -> dict:
    """
    Aggregate sentence-level scores to essay level by taking the mean of
    P(formal) and P(informal) across all sentences.
    """
    formal_scores   = [s["formal"]   for s in formality_scores]
    informal_scores = [s["informal"] for s in formality_scores]
    return {
        "formal":   float(np.mean(formal_scores)),
        "informal": float(np.mean(informal_scores)),
    }


# ── Public API ───────────────────────────────────────────────────────────────

def analyze(text: str) -> dict:
    """
    Compute essay-level formality scores for a single text.

    Returns:
        {
            "formal":           float,   # mean P(formal)  across sentences  [0, 1]
            "informal":         float,   # mean P(informal) across sentences [0, 1]
            "sentence_count":   int,
            "sentence_scores":  list[dict]   # per-sentence {"formal", "informal"}
        }
    """
    sentences = _split_into_sentences(text)
    if not sentences:
        return {
            "formal": 0.0,
            "informal": 0.0,
            "sentence_count": 0,
            "sentence_scores": [],
        }

    scores     = _get_formality_scores(sentences)
    mean       = _get_mean_formality_scores(scores)

    return {
        "formal":          round(mean["formal"],   6),
        "informal":        round(mean["informal"], 6),
        "sentence_count":  len(sentences),
        "sentence_scores": [
            {"formal": round(s["formal"], 6), "informal": round(s["informal"], 6)}
            for s in scores
        ],
    }


def compare(text1: str, text2: str) -> dict:
    """
    Compute formality scores for both texts and the delta (text2 − text1).

    This mirrors the notebook's `delta_formality = humanized_formality - AI_formality`.

    Returns:
        {
            "text1":           { "formal", "informal", "sentence_count", "sentence_scores" },
            "text2":           { "formal", "informal", "sentence_count", "sentence_scores" },
            "delta_formality": float   # positive → text2 is more formal than text1
        }
    """
    scores1 = analyze(text1)
    scores2 = analyze(text2)

    delta = round(scores2["formal"] - scores1["formal"], 6)

    return {
        "text1":           scores1,
        "text2":           scores2,
        "delta_formality": delta,
    }
