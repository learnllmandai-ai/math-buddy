import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

from tutoring.prompts import GRADE_PROMPTS


def build_chain(grade):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        raise ValueError(
            "Missing Gemini API key. Add GEMINI_API_KEY=... to your .env file "
            "or set GOOGLE_API_KEY in the environment."
        )

    llm = ChatGoogleGenerativeAI(
        model=model,
        temperature=0.3,
        api_key=api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GRADE_PROMPTS[grade]),
            ("human", "{question}"),
        ]
    )

    return prompt | llm
