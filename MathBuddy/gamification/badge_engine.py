"""Badge logic."""

BADGES = {
    "First Question": 10,
    "Math Explorer": 100,
    "Problem Solver": 500,
    "Math Champion": 1000,
}


def earned_badges(xp_total: int) -> list:
    """Return the badges unlocked by the current XP total."""
    return [name for name, threshold in BADGES.items() if xp_total >= threshold]
