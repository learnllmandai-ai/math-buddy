"""Adaptive difficulty helpers."""


def determine_difficulty(mastery_score: float) -> str:
    """Map a mastery percentage to an adaptive difficulty label."""
    if mastery_score >= 85:
        return "hard"
    if mastery_score >= 60:
        return "medium"
    return "easy"


def build_difficulty_rules(mastery_score: float) -> str:
    """Build a short prompt rule for the current difficulty level."""
    difficulty = determine_difficulty(mastery_score)
    if difficulty == "hard":
        return "Give a challenging problem and ask for a deeper explanation."
    if difficulty == "medium":
        return "Give a balanced problem and ask for one clear next step."
    return "Give a simple, friendly example and ask a guiding question."
