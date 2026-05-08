"""
feedback_engine.py
NLP-based answer analysis using NLTK and TextBlob.
"""

from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import string
import re

# Download required NLTK data (safe to call repeatedly)
for pkg in ["punkt", "stopwords", "averaged_perceptron_tagger", "punkt_tab"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

STOP_WORDS = set(stopwords.words("english"))

# ─────────────────────────────────────────────────────────────
# Confidence phrases boost sentiment score
# ─────────────────────────────────────────────────────────────
CONFIDENCE_PHRASES = [
    "i have experience", "i successfully", "i led", "i built",
    "i designed", "i implemented", "i achieved", "in my experience",
    "for example", "for instance", "specifically", "i demonstrated",
    "i improved", "i delivered", "i managed",
]

WEAK_PHRASES = [
    "i think maybe", "i'm not sure", "i don't really know",
    "i guess", "kind of", "sort of", "i might", "not really",
]


def analyze_answer(answer: str, question: str, role_keywords: dict) -> dict:
    """
    Full NLP analysis of the candidate's answer.

    Returns a dict with scores and feedback messages.
    """
    results = {}
    answer_lower = answer.lower().strip()

    # ── 1. Length score ──────────────────────────────────────
    word_count = len(answer.split())
    sentences   = sent_tokenize(answer)
    sent_count  = len(sentences)

    if word_count < 15:
        length_score = 1
        length_msg   = "Way too short – aim for at least 50 words with a clear example."
    elif word_count < 40:
        length_score = 4
        length_msg   = "Too brief. Expand with a specific example or result."
    elif word_count < 80:
        length_score = 7
        length_msg   = "Decent length. Adding one more concrete example would strengthen it."
    elif word_count <= 180:
        length_score = 10
        length_msg   = "Excellent answer length – detailed yet focused."
    else:
        length_score = 7
        length_msg   = "Very detailed, but consider trimming for clarity and conciseness."

    results.update({
        "length_score": length_score,
        "length_msg":   length_msg,
        "word_count":   word_count,
        "sent_count":   sent_count,
    })

    # ── 2. Sentiment / confidence ────────────────────────────
    blob      = TextBlob(answer)
    polarity  = blob.sentiment.polarity
    subj      = blob.sentiment.subjectivity

    confidence_hits = sum(1 for p in CONFIDENCE_PHRASES if p in answer_lower)
    weak_hits       = sum(1 for p in WEAK_PHRASES        if p in answer_lower)

    base_sent = 7 if polarity >= 0 else 4
    sentiment_score = min(10, max(1,
        base_sent + (confidence_hits * 1) - (weak_hits * 2)
    ))

    if sentiment_score >= 8:
        sentiment_msg = "Confident, assertive tone – great!"
    elif sentiment_score >= 6:
        sentiment_msg = "Reasonably confident. Try adding 'I successfully…' style statements."
    else:
        sentiment_msg = "Tone sounds uncertain. Replace hedging words with assertive language."

    results.update({
        "sentiment_score": sentiment_score,
        "sentiment_msg":   sentiment_msg,
        "polarity":        round(polarity, 2),
        "subjectivity":    round(subj,     2),
        "confidence_hits": confidence_hits,
        "weak_hits":       weak_hits,
    })

    # ── 3. Keyword matching ──────────────────────────────────
    tokens = word_tokenize(answer_lower)
    tokens = [t for t in tokens if t not in STOP_WORDS and t not in string.punctuation]

    matched_topics = []
    raw_kw_score   = 0

    for topic, keywords in role_keywords.items():
        hits = [kw for kw in keywords if kw in answer_lower]
        if hits:
            matched_topics.append(f"{topic} ({', '.join(hits[:3])})")
            raw_kw_score += len(hits)

    keyword_score = min(int(raw_kw_score * 1.8), 10)
    results.update({
        "keyword_score":  keyword_score,
        "matched_topics": matched_topics,
        "raw_kw_score":   raw_kw_score,
    })

    # ── 4. Structure / readability ───────────────────────────
    has_example = bool(re.search(
        r"\b(for example|for instance|such as|e\.g\.|in my|when i|"
        r"i once|a situation|a project|we built|i worked)\b",
        answer_lower
    ))
    has_result = bool(re.search(
        r"\b(result|outcome|impact|reduced|increased|improved|saved|"
        r"achieved|delivered|launched|decreased)\b",
        answer_lower
    ))
    structure_score = 5
    if has_example: structure_score += 3
    if has_result:  structure_score += 2
    structure_score = min(structure_score, 10)

    results.update({
        "structure_score": structure_score,
        "has_example":     has_example,
        "has_result":      has_result,
    })

    # ── 5. Overall weighted score ────────────────────────────
    overall = round(
        length_score   * 0.25 +
        sentiment_score * 0.25 +
        keyword_score  * 0.30 +
        structure_score * 0.20,
        1
    )
    results["overall_score"] = overall

    # ── 6. Improvement tips ──────────────────────────────────
    tips = []
    if word_count < 50:
        tips.append("Expand your answer – aim for 60-150 words with a concrete example.")
    if weak_hits > 0:
        tips.append("Remove hedging phrases ('I guess', 'kind of'). Speak assertively.")
    if confidence_hits == 0:
        tips.append("Open with 'In my experience…' or 'I have successfully…' to project confidence.")
    if keyword_score < 4:
        tips.append("Include more domain-specific keywords relevant to this role.")
    if not has_example:
        tips.append("Add a specific example: 'For instance, in my last project…'")
    if not has_result:
        tips.append("Quantify your impact: 'This reduced load time by 40%' is more powerful.")
    if subj > 0.75:
        tips.append("Balance opinion with facts and measurable outcomes.")
    if not tips:
        tips.append("Strong answer! Keep this structure for all behavioural questions.")

    results["tips"] = tips[:4]   # cap at 4 tips

    # ── 7. Grade label ───────────────────────────────────────
    if overall >= 8.5:
        results["grade"] = "Excellent"
    elif overall >= 7:
        results["grade"] = "Good"
    elif overall >= 5:
        results["grade"] = "Average"
    else:
        results["grade"] = "Needs Work"

    return results
