def enforce_pedagogy(student_input):
    forbidden_phrases = [
        "give me answer",
        "just answer",
        "solve it completely",
    ]

    lowered = student_input.lower()

    for phrase in forbidden_phrases:
        if phrase in lowered:
            return """
            Remember 😊

            Learning works best when you try first.

            What is the first step you think we should take?
            """

    return None
