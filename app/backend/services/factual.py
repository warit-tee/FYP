import json
import time

from utils.model_cache import get_openai_client


# ── Core QG → QA → Evaluation Pipeline ────────────────────────────────────────


def _call_llm(prompt: str) -> str:
    """
    Calls the Azure OpenAI (GPT) API with the given prompt.
    Includes a small sleep to respect rate limits.
    Returns the raw text response, or "{}" on failure.
    """
    client = get_openai_client()
    if client is None:
        return "{}"

    time.sleep(0.5)  # basic rate-limiting buffer

    try:
        from utils.model_cache import get_openai_deployment
        deployment = get_openai_deployment()

        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception as exc:
        print(f"[factual] LLM call failed: {exc}")
        return "{}"


def _generate_questions(source_text: str, num_questions: int = 10) -> list[dict]:
    """
    Step 1 – Generate factual Q&A pairs grounded in *source_text*.

    Returns a list of dicts:  [{"question": "...", "answer": "..."}, ...]
    Returns [] on any failure.
    """
    prompt = f"""
You are a factual consistency evaluator.
Read the following text (Source Essay) and generate {num_questions} specific,
factual questions that can be answered based on the text.
For each question, provide the correct answer as found in the text.

Output format must be valid JSON (no markdown fences):
[
    {{"question": "Question 1?", "answer": "Answer 1"}},
    {{"question": "Question 2?", "answer": "Answer 2"}}
]

Source Essay:
{source_text}
"""
    response = _call_llm(prompt)
    try:
        clean = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return []


def _answer_with_context(context_text: str, question: str) -> str:
    """
    Step 2 – Answer *question* using only *context_text* as the knowledge source.
    Returns "Information not found" when the context doesn't contain the answer.
    """
    prompt = f"""
Answer the question based ONLY on the provided Context.
If the information is not present in the context, say "Information not found".

Context:
{context_text}

Question:
{question}

Answer:
"""
    return _call_llm(prompt)


def _evaluate_consistency(ground_truth: str, candidate_answer: str, question: str) -> dict:
    """
    Step 3 – Decide whether *candidate_answer* is factually consistent with
    *ground_truth* for the given *question*.

    Returns {"is_consistent": bool, "reason": str}.
    """
    prompt = f"""
Question: {question}

Ground Truth Answer: {ground_truth}
Candidate Answer: {candidate_answer}

Task: Determine if the Candidate Answer is factually consistent with the
Ground Truth Answer. Does the candidate preserve the key fact?

Respond with JSON only (no markdown fences):
{{"is_consistent": true, "reason": "Explanation"}}
"""
    response = _call_llm(prompt)
    try:
        clean = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception:
        return {"is_consistent": False, "reason": "Error parsing LLM response"}


# ── Public API ─────────────────────────────────────────────────────────────────


def analyze(
    source_text: str,
    candidate_text: str,
    num_questions: int = 10,
) -> dict:
    """
    Run the full QG → QA → Eval pipeline.

    *source_text*    – the reference / ground-truth essay (questions are
                       generated FROM this text).
    *candidate_text* – the essay being evaluated (questions are ANSWERED
                       against this text).
    *num_questions*  – how many factual questions to generate (default 10).

    Returns:
    {
        "score":   float,       # fraction of consistent answers  [0.0 – 1.0]
        "details": [            # one entry per question
            {
                "question":     str,
                "ground_truth": str,
                "candidate_answer": str,
                "is_consistent":    bool,
                "reason":           str,
            },
            ...
        ]
    }
    """
    qa_pairs = _generate_questions(source_text, num_questions=num_questions)

    if not qa_pairs:
        return {"score": None, "error": "Failed to generate questions", "details": []}

    details = []
    correct = 0

    for item in qa_pairs:
        q = item.get("question", "")
        gt_answer = item.get("answer", "")

        candidate_answer = _answer_with_context(candidate_text, q)
        eval_result = _evaluate_consistency(gt_answer, candidate_answer, q)

        is_consistent = eval_result.get("is_consistent", False)
        if is_consistent:
            correct += 1

        details.append(
            {
                "question": q,
                "ground_truth": gt_answer,
                "candidate_answer": candidate_answer,
                "is_consistent": is_consistent,
                "reason": eval_result.get("reason", ""),
            }
        )

    score = round(correct / len(qa_pairs), 6) if qa_pairs else None
    return {"score": score, "details": details}


def compare(ai_text: str, humanized_text: str, num_questions: int = 10) -> dict:
    """
    Convenience wrapper that runs the pipeline in BOTH directions:

    *forward*  – questions generated from *ai_text*,    answered by *humanized_text*
    *reversed* – questions generated from *humanized_text*, answered by *ai_text*

    Returns:
    {
        "forward":  {"score": float, "details": [...]},
        "reversed": {"score": float, "details": [...]},
    }
    """
    forward = analyze(
        source_text=ai_text,
        candidate_text=humanized_text,
        num_questions=num_questions,
    )
    reversed_ = analyze(
        source_text=humanized_text,
        candidate_text=ai_text,
        num_questions=num_questions,
    )
    return {"forward": forward, "reversed": reversed_}
