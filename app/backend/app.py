from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from models.essay import Essay

load_dotenv()

app = Flask(__name__)
CORS(app)


# ── helpers ────────────────────────────────────────────────────────────────


def parse_essays(body: dict) -> tuple[Essay, Essay]:
    """Extract and validate both essays from the request body."""
    ai_text        = body.get("ai_text", "").strip()
    humanized_text = body.get("humanized_text", "").strip()

    if not ai_text or not humanized_text:
        raise ValueError("Both 'ai_text' and 'humanized_text' are required")

    return Essay(ai_text, label="ai"), Essay(humanized_text, label="humanized")


# ── routes ─────────────────────────────────────────────────────────────────


@app.route("/")
def home():
    return jsonify({"message": "Essay Analysis API is running"})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/compare", methods=["POST"])
def compare():
    """
    Cosine similarity + difference between the two essays.

    Body:  { "ai_text": "...", "humanized_text": "..." }

    Response:
    {
        "similarity": { "tfidf": 0.87, "sbert": 0.92, "nemotron": 0.88 },
        "difference": { "tfidf": 0.13, "sbert": 0.08, "nemotron": 0.12 }
    }
    """
    try:
        ai_essay, human_essay = parse_essays(request.get_json(force=True))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(ai_essay.compare(human_essay))


@app.route("/detectability", methods=["POST"])
def detectability():
    """
    AI-detectability scores from Sapling (web-scraped) and ZeroGPT for each essay.

    Body:  { "ai_text": "...", "humanized_text": "..." }

    Response:
    {
        "ai":        { "sapling": {...}, "zerogpt": {...} },
        "humanized": { "sapling": {...}, "zerogpt": {...} }
    }
    """
    try:
        ai_essay, human_essay = parse_essays(request.get_json(force=True))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "ai":       ai_essay.get_detectability(),
        "humanized": human_essay.get_detectability(),
    })


@app.route("/emotions", methods=["POST"])
def emotions():
    """
    Ekman emotion scores for each essay.

    Body:  { "ai_text": "...", "humanized_text": "..." }

    Response:
    {
        "ai":        [ { "label": "neutral", "score": 0.62 }, ... ],
        "humanized": [ ... ]
    }
    """
    try:
        ai_essay, human_essay = parse_essays(request.get_json(force=True))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "ai":       ai_essay.get_emotions(),
        "humanized": human_essay.get_emotions(),
    })


@app.route("/full-analysis", methods=["POST"])
def full_analysis():
    """
    Runs all three analyses in one request.

    Body:  { "ai_text": "...", "humanized_text": "..." }

    Response:
    {
        "comparison":  { "similarity": {...}, "difference": {...} },
        "ai":          { "label": "ai",        "detectability": {...}, "emotions": [...] },
        "humanized":   { "label": "humanized", "detectability": {...}, "emotions": [...] }
    }
    """
    try:
        ai_essay, human_essay = parse_essays(request.get_json(force=True))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "comparison": ai_essay.compare(human_essay),
        "ai":         ai_essay.to_dict(),
        "humanized":  human_essay.to_dict(),
    })


# ── entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)