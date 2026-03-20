from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

from models.essay import Essay
from services import factual as factual_svc
from services import tone

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
        "similarity": { "tfidf": 0.87, "sbert": 0.92 },
        "difference": { "tfidf": 0.13, "sbert": 0.08 }
        # "similarity": { "tfidf": 0.87, "sbert": 0.92, "nemotron": 0.88 },
        # "difference": { "tfidf": 0.13, "sbert": 0.08, "nemotron": 0.12 }
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


@app.route("/tone", methods=["POST"])
def tone_route():
    """
    Formality scores for each essay and the delta (humanized − AI).

    Body:  { "ai_text": "...", "humanized_text": "..." }

    Response:
    {
        "ai": {
            "formal":          float,
            "informal":        float,
            "sentence_count":  int,
            "sentence_scores": [ {"formal": float, "informal": float}, ... ]
        },
        "humanized": { ... },
        "delta_formality": float   # positive → humanized is more formal
    }
    """
    try:
        ai_essay, human_essay = parse_essays(request.get_json(force=True))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    result = tone.compare(ai_essay.text, human_essay.text)

    return jsonify({
        "ai":              result["text1"],
        "humanized":       result["text2"],
        "delta_formality": result["delta_formality"],
    })


@app.route("/factual", methods=["POST"])
def factual():
    """
    Factual consistency scores using an LLM-based QG → QA → Eval pipeline.

    Runs in BOTH directions (forward & reversed) mirroring the methodology
    in fact.ipynb.

    Body:
    {
        "ai_text":        "...",
        "humanized_text": "...",
        "num_questions":  10       # optional, default 10
    }

    Response:
    {
        "forward": {
            "score":   float,      # questions from ai_text, answered by humanized_text
            "details": [
                {
                    "question":          str,
                    "ground_truth":      str,
                    "candidate_answer":  str,
                    "is_consistent":     bool,
                    "reason":            str
                },
                ...
            ]
        },
        "reversed": {
            "score":   float,      # questions from humanized_text, answered by ai_text
            "details": [ ... ]
        }
    }
    """
    try:
        ai_essay, human_essay = parse_essays(request.get_json(force=True))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    body = request.get_json(force=True) or {}
    num_questions = int(body.get("num_questions", 10))

    result = factual_svc.compare(
        ai_text=ai_essay.text,
        humanized_text=human_essay.text,
        num_questions=num_questions,
    )

    return jsonify(result)


@app.route("/full-analysis", methods=["POST"])
def full_analysis():
    """
    Runs all analyses (comparison, detectability, emotions, tone, factual)
    in one request.

    Body:  { "ai_text": "...", "humanized_text": "...", "num_questions": 10 }

    Response:
    {
        "comparison":  { "similarity": {...}, "difference": {...} },
        "tone": {
            "ai":              { "formal", "informal", "sentence_count", "sentence_scores" },
            "humanized":       { ... },
            "delta_formality": float
        },
        "factual": {
            "forward":  { "score": float, "details": [...] },
            "reversed": { "score": float, "details": [...] }
        },
        "ai":        { "label": "ai",        "detectability": {...}, "emotions": [...] },
        "humanized": { "label": "humanized", "detectability": {...}, "emotions": [...] }
    }
    """
    try:
        ai_essay, human_essay = parse_essays(request.get_json(force=True))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    body = request.get_json(force=True) or {}
    num_questions = int(body.get("num_questions", 10))

    tone_result = tone.compare(ai_essay.text, human_essay.text)

    factual_result = factual_svc.compare(
        ai_text=ai_essay.text,
        humanized_text=human_essay.text,
        num_questions=num_questions,
    )

    return jsonify({
        "comparison": ai_essay.compare(human_essay),
        "tone": {
            "ai":              tone_result["text1"],
            "humanized":       tone_result["text2"],
            "delta_formality": tone_result["delta_formality"],
        },
        "factual": factual_result,
        "ai":       ai_essay.to_dict(),
        "humanized": human_essay.to_dict(),
    })


# ── entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)