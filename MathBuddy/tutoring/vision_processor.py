from PIL import Image

VISION_PROMPT = """
Step 1:
Convert handwriting into valid LaTeX.

Step 2:
Identify math topic.

Step 3:
Ask exactly one guiding question.

Do NOT provide final answer.
"""


def process_image(uploaded_image):
    image = Image.open(uploaded_image)
    return image
