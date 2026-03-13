from services import similarity, detectability, emotions


class Essay:
    """
    Represents a single essay and exposes analysis methods.
    Results are lazy-evaluated and cached on the instance so
    each service is only called once per Essay object.
    """

    def __init__(self, text: str, label: str = ""):
        if not text or not text.strip():
            raise ValueError("Essay text cannot be empty")
        self.text  = text.strip()
        self.label = label

        # private cache — populated on first access
        self._emotions       = None
        self._detectability  = None

    # ── analysis methods ────────────────────────────────────────────────────

    def get_emotions(self) -> list[dict]:
        if self._emotions is None:
            self._emotions = emotions.analyze(self.text)
        return self._emotions

    def get_detectability(self) -> dict:
        if self._detectability is None:
            self._detectability = detectability.all_detectors(self.text)
        return self._detectability

    def compare(self, other: "Essay") -> dict:
        """Compute cosine similarity/difference against another Essay."""
        return similarity.all_methods(self.text, other.text)

    # ── serialization ───────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Full profile: detectability + emotions for this essay."""
        return {
            "label":          self.label,
            "detectability":  self.get_detectability(),
            "emotions":       self.get_emotions(),
        }

    def __repr__(self) -> str:
        preview = self.text[:60].replace("\n", " ")
        return f'Essay(label={self.label!r}, text={preview!r}...)'
