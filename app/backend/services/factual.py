import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    qa_pairs = _generate_questions(source_text, num_questions=num_questions)

    if not qa_pairs:
        return {"score": None, "error": "Failed to generate questions", "details": []}

    def _process_question(item: dict) -> dict:
        q = item.get("question", "")
        gt_answer = item.get("answer", "")
        candidate_answer = _answer_with_context(candidate_text, q)
        eval_result = _evaluate_consistency(gt_answer, candidate_answer, q)
        is_consistent = eval_result.get("is_consistent", False)
        return {
            "question": q,
            "ground_truth": gt_answer,
            "candidate_answer": candidate_answer,
            "is_consistent": is_consistent,
            "reason": eval_result.get("reason", ""),
        }

    # Run all questions concurrently — cap workers to avoid hammering the API
    max_workers = min(len(qa_pairs), 5)
    results_map: dict[int, dict] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_question, item): i for i, item in enumerate(qa_pairs)}
        for future in as_completed(futures):
            idx = futures[future]
            results_map[idx] = future.result()

    # Restore original question order
    details = [results_map[i] for i in range(len(qa_pairs))]
    correct = sum(1 for d in details if d["is_consistent"])
    score = round(correct / len(qa_pairs), 6)
    return {"score": score, "details": details}


def compare(ai_text: str, humanized_text: str, num_questions: int = 10) -> dict:
    with ThreadPoolExecutor(max_workers=2) as executor:
        forward_future  = executor.submit(analyze, ai_text, humanized_text, num_questions)
        reversed_future = executor.submit(analyze, humanized_text, ai_text, num_questions)
        forward  = forward_future.result()
        reversed_ = reversed_future.result()

    return {"forward": forward, "reversed": reversed_}
