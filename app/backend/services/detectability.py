import os
import requests
import logging


# ── Sapling (official API) ─────────────────────────────────────────────────
# Docs: https://sapling.ai/docs/api/detector
# Endpoint: POST https://api.sapling.ai/api/v1/aidetect
# Requires a 32-character API key in the environment variable SAPLING_API_KEY.

def sapling(text: str) -> dict:
    """
    Query the Sapling AI detector via the official REST API.

    Returns:
        {
            "score":           float,   # 0.0 = human, 1.0 = AI
            "sentence_scores": [{"sentence": str, "score": float}, ...],
        }
    on success, or {"error": str} on failure.

    Requires env var:  SAPLING_API_KEY
    """
    api_key = os.getenv("SAPLING_API_KEY")
    if not api_key:
        return {"error": "SAPLING_API_KEY is not set"}

    try:
        resp = requests.post(
            "https://api.sapling.ai/api/v1/aidetect",
            json={
                "key":         api_key,
                "text":        text
            },
            timeout=30,
        )

        if 200 <= resp.status_code < 300:
            data = resp.json()
            return {
                "score":           round(float(data["score"]), 4),
                "sentence_scores": data.get("sentence_scores"),
            }

        # surface the error message Sapling returns in the body
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        return {"error": f"Sapling returned {resp.status_code}", "detail": detail}

    except Exception as exc:
        return {"error": str(exc)}


# ── ZeroGPT (API-style request) ────────────────────────────────────────────

def zerogpt(text: str) -> dict:
    try:
        resp = requests.post(
            "https://api.zerogpt.com/api/detect/detectText",
            headers={
                "Content-Type": "application/json",
                "Origin":       "https://www.zerogpt.com",
                "Referer":      "https://www.zerogpt.com/",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                ),
            },
            json={"text": text, "input_text": text},
            timeout=20,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                d = data.get("data", {})
                return {
                    "fake_percentage": d.get("fakePercentage"),
                    "is_human":        d.get("isHuman"),
                    "ai_words":        d.get("aiWords"),
                    "text_words":      d.get("textWords"),
                    "feedback":        d.get("feedback"),
                }
            return {"error": "ZeroGPT returned success=False", "raw": data}
        return {"error": f"ZeroGPT returned {resp.status_code}: {resp.text}"}
    except Exception as exc:
        return {"error": str(exc)}


# ── Combined ────────────────────────────────────────────────────────────────

def all_detectors(text: str) -> dict:
    return {
        "sapling": sapling(text),
        "zerogpt": zerogpt(text),
    }