from utils.model_cache import get_emotion_pipeline


def analyze(text: str) -> list[dict]:
    """
    Returns 7 Ekman emotion scores sorted by confidence (descending).
    Input is truncated to 512 tokens — the model's context limit.
    """
    pipe = get_emotion_pipeline()
    results = pipe(text[:512])
    # pipeline returns list-of-lists when top_k=None
    scores = results[0] if isinstance(results[0], list) else results
    return sorted(scores, key=lambda x: x["score"], reverse=True)
