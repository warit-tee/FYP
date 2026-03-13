import os
import numpy as np
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.model_cache import get_sbert


def tfidf_similarity(text1: str, text2: str) -> float:
    vec = TfidfVectorizer()
    tfidf = vec.fit_transform([text1, text2])
    return float(cosine_similarity(tfidf[0], tfidf[1])[0][0])


def sbert_similarity(text1: str, text2: str) -> float:
    model = get_sbert()
    emb1, emb2 = model.encode([text1, text2])
    sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return float(sim)


def nemotron_similarity(text1: str, text2: str) -> tuple[float | None, str | None]:
    """
    Returns (similarity_score, error_message).
    error_message is None on success; score is None on failure.
    """
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("NEMOTRON_API_KEY")
    if not api_key:
        return None, "NVIDIA_API_KEY not set in environment"

    base_url = os.getenv("NEMOTRON_BASE_URL", "https://integrate.api.nvidia.com/v1")

    def get_embedding(text: str) -> np.ndarray:
        resp = requests.post(
            f"{base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "nvidia/llama-3.1-nemotron-8b-instruct",
                "input": text,
                "encoding_format": "float",
            },
            timeout=30,
        )
        resp.raise_for_status()
        return np.array(resp.json()["data"][0]["embedding"])

    try:
        emb1 = get_embedding(text1)
        emb2 = get_embedding(text2)
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(sim), None
    except Exception as exc:
        return None, str(exc)


def all_methods(text1: str, text2: str) -> dict:
    tfidf = tfidf_similarity(text1, text2)
    sbert = sbert_similarity(text1, text2)
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
            "nemotron": round(1 - nem, 6) if nem is not None else None,
        },
    }
    if nem_err:
        result["nemotron_error"] = nem_err
    return result
