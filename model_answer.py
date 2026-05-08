"""
model_answer.py
Uses the Google Gemini API to generate ideal interview answers
and personalised coaching feedback.
"""

import os
import google.generativeai as genai


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _get_model() -> genai.GenerativeModel:
    """Configure the Gemini API and return a model instance; raises if API key is missing."""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not set. "
            "Enter it in the sidebar or set the environment variable."
        )
    
    genai.configure(api_key=api_key)
    # Using gemini-1.5-flash as it is fast and ideal for standard text generation
    return genai.GenerativeModel("gemini-1.5-flash")


# ─────────────────────────────────────────────────────────────
# Public functions
# ─────────────────────────────────────────────────────────────

def get_model_answer(question: str, role: str, user_answer: str = "") -> str:
    """
    Generate a structured ideal answer for the interview question.

    Args:
        question:    The interview question.
        role:        Target job role.
        user_answer: Optional – the candidate's attempt (for comparison tips).

    Returns:
        Formatted string with three sections:
        1. Ideal model answer
        2. Key points that must be included
        3. One thing to avoid
    """
    candidate_context = (
        f"\n\nCandidate's attempt:\n{user_answer}\n\n"
        "After the model answer, briefly note one specific thing the candidate "
        "did well and one thing to improve."
        if user_answer else ""
    )

    prompt = f"""You are a senior interview coach specialising in {role} roles.

Interview question: {question}{candidate_context}

Provide your response in exactly three clearly labelled sections:

**1. Model Answer**
A confident, structured answer (4–6 sentences). Use the STAR method where appropriate (Situation, Task, Action, Result).

**2. Key Points to Include**
A short list (3–5 bullets) of the concepts or keywords that must appear in a strong answer.

**3. One Thing to Avoid**
One specific mistake or weak phrasing candidates often use for this question.
"""

    model = _get_model()
    response = model.generate_content(prompt)
    return response.text


def get_quick_tip(question: str, role: str) -> str:
    """Return a single actionable tip (≤ 25 words) for the question."""
    prompt = (
        f"Give ONE actionable interview tip (max 25 words) for answering: "
        f"'{question}' for a {role} position. No preamble."
    )
    
    model = _get_model()
    response = model.generate_content(prompt)
    return response.text.strip()


def get_overall_coaching(
    role: str,
    questions: list,
    answers: list,
    scores: list,
) -> str:
    """
    Generate a holistic coaching report after all questions are answered.

    Args:
        role:      Target role.
        questions: List of question strings.
        answers:   List of candidate answer strings (same order as questions).
        scores:    List of overall float scores (same order).

    Returns:
        A coaching narrative (3–4 paragraphs).
    """
    qa_pairs = "\n\n".join(
        f"Q{i+1} (score {scores[i]}/10): {q}\nAnswer: {a}"
        for i, (q, a) in enumerate(zip(questions, answers))
    )

    prompt = f"""You are a senior interview coach. 
Role: {role}
Candidate's interview session:
{qa_pairs}

Write a 3-paragraph coaching report:
1. Overall performance summary (strengths observed).
2. Top 2–3 specific areas to improve with actionable advice.
3. One encouraging closing statement about their readiness.

Keep the tone warm, professional, and motivating. No bullet points."""

    model = _get_model()
    response = model.generate_content(prompt)
    return response.text
