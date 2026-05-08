import random

# ─────────────────────────────────────────────────────────────
# Question bank  –  grouped by role
# ─────────────────────────────────────────────────────────────
QUESTIONS = {
    "Software Developer": [
        "Explain the difference between OOP and functional programming.",
        "What is a RESTful API? Give a real-world example.",
        "How do you handle version control in a team project?",
        "Describe the SOLID principles with examples.",
        "What is time complexity? Explain O(n log n).",
        "How would you debug a critical production issue at 2 AM?",
        "What is Docker and why is it used in modern development?",
        "Explain recursion with a practical example.",
        "What is the difference between SQL and NoSQL databases?",
        "How do you ensure code quality in your projects?",
    ],
    "HR Manager": [
        "How do you handle conflicts between team members?",
        "Describe your recruitment process for a senior role.",
        "What KPIs do you track in the HR department?",
        "How do you ensure employee engagement and retention?",
        "Describe a time you managed a particularly difficult employee situation.",
        "What is your approach to performance reviews?",
        "How do you handle confidential employee information?",
        "Describe a successful onboarding programme you designed.",
    ],
    "Data Scientist": [
        "What is overfitting and how do you prevent it?",
        "Explain the bias-variance tradeoff.",
        "When would you use Random Forest vs XGBoost?",
        "How do you handle missing data in a dataset?",
        "Explain k-fold cross-validation and why it matters.",
        "What is feature engineering? Give an example.",
        "How would you explain a machine learning model to a non-technical stakeholder?",
        "Describe the steps in a typical data science project.",
    ],
    "Product Manager": [
        "How do you prioritize features in a product roadmap?",
        "Describe how you would run a sprint planning session.",
        "How do you measure product success?",
        "Walk me through a product you have built from scratch.",
        "How do you gather and validate user requirements?",
        "Describe a time a product launch did not go as planned.",
        "How do you align engineering and business stakeholders?",
        "What frameworks do you use for product discovery?",
    ],
}

# ─────────────────────────────────────────────────────────────
# Keywords to look for in answers  –  grouped by role + topic
# ─────────────────────────────────────────────────────────────
KEYWORDS = {
    "Software Developer": {
        "oop / functional":    ["object", "class", "inheritance", "encapsulation",
                                "polymorphism", "immutable", "pure function", "lambda"],
        "api / rest":          ["endpoint", "request", "response", "http", "rest",
                                "json", "status code", "authentication"],
        "version control":     ["git", "commit", "branch", "merge", "pull request",
                                "conflict", "rebase", "tag"],
        "solid principles":    ["single responsibility", "open closed", "liskov",
                                "interface segregation", "dependency inversion"],
        "debugging":           ["log", "stack trace", "reproduce", "isolate",
                                "rollback", "monitoring", "alert"],
        "docker / containers": ["container", "image", "compose", "kubernetes",
                                "orchestration", "microservice", "deploy"],
    },
    "HR Manager": {
        "conflict resolution": ["mediation", "communication", "resolution",
                                "empathy", "listen", "neutral", "facilitate"],
        "recruitment":         ["screening", "interview", "onboarding", "job description",
                                "candidate", "assessment", "pipeline"],
        "performance":         ["kpi", "review", "feedback", "goal", "okr",
                                "appraisal", "development plan"],
        "engagement":          ["culture", "retention", "motivation", "recognition",
                                "survey", "wellbeing", "inclusion"],
    },
    "Data Scientist": {
        "overfitting":         ["regularization", "cross-validation", "dropout",
                                "training", "test", "validation", "pruning"],
        "bias variance":       ["underfitting", "complexity", "error", "tradeoff",
                                "generalize", "model selection"],
        "models":              ["random forest", "xgboost", "gradient boosting",
                                "ensemble", "decision tree", "hyperparameter"],
        "data prep":           ["missing", "imputation", "normaliz", "encode",
                                "feature", "outlier", "clean"],
    },
    "Product Manager": {
        "prioritization":      ["impact", "effort", "value", "stakeholder",
                                "roadmap", "mvp", "rice", "moscow"],
        "agile / sprint":      ["scrum", "sprint", "backlog", "velocity",
                                "standup", "retrospective", "epic", "story"],
        "metrics":             ["kpi", "dau", "mau", "retention", "churn",
                                "nps", "conversion", "revenue"],
        "user research":       ["user", "persona", "interview", "survey",
                                "prototype", "usability", "feedback"],
    },
}


def get_questions(role: str, n: int = 5) -> list:
    """Return n random questions for the given role."""
    pool = QUESTIONS.get(role, QUESTIONS["Software Developer"])
    return random.sample(pool, min(n, len(pool)))


def get_keywords(role: str) -> dict:
    """Return keyword dict for the given role."""
    return KEYWORDS.get(role, {})


def get_all_roles() -> list:
    return list(QUESTIONS.keys())
