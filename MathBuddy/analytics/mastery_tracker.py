"""Topic-level mastery tracking helpers."""


def compute_mastery(correct_steps: int, total_steps: int) -> float:
    """Return a mastery percentage based on correct steps over total steps."""
    if total_steps <= 0:
        return 0.0
    return round((correct_steps / total_steps) * 100, 1)


def update_topic_mastery(topic_scores: dict, topic: str, correct_steps: int, total_steps: int) -> dict:
    """Update or initialize a topic mastery score in a dictionary."""
    topic_scores[topic] = compute_mastery(correct_steps, total_steps)
    return topic_scores
