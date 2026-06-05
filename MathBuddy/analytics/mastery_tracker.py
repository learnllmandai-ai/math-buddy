def compute_mastery(correct_answers: int, total_questions: int) -> float:
    """
    Calculates the mastery percentage based on correct answers and total questions.
    Returns 0.0 if total_questions is 0.
    """
    if total_questions == 0:
        return 0.0
    return (correct_answers / total_questions) * 100.0

def update_topic_mastery(current_mastery_scores: dict, topic: str, correct: int, total: int, learning_rate: float = 0.2) -> dict:
    """
    Updates the mastery score for a given topic using a simple exponential moving average.
    
    Args:
        current_mastery_scores (dict): A dictionary where keys are topic names (str)
                                       and values are their current mastery percentages (float).
        topic (str): The name of the topic to update.
        correct (int): Number of correct answers in the latest interaction for this topic.
        total (int): Total number of questions in the latest interaction for this topic.
        learning_rate (float): The weight given to the new performance (between 0 and 1).
                               A higher value means new performance has a greater impact.

    Returns:
        dict: The updated dictionary of mastery scores.
    """
    updated_scores = current_mastery_scores.copy()

    if total == 0:
        # If no questions were asked, no change in mastery for this interaction
        return updated_scores

    latest_performance_percentage = (correct / total) * 100.0

    if topic not in updated_scores:
        updated_scores[topic] = latest_performance_percentage
    else:
        old_mastery = updated_scores[topic]
        new_mastery = (1 - learning_rate) * old_mastery + learning_rate * latest_performance_percentage
        updated_scores[topic] = new_mastery
        
    return updated_scores