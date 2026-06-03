"""XP and reward helpers."""


def award_xp(correct_step: bool) -> int:
    """Return XP earned for a correct step."""
    return 10 if correct_step else 2


def total_xp(xp_history: list) -> int:
    """Sum earned XP points from a simple history list."""
    return sum(xp_history)
