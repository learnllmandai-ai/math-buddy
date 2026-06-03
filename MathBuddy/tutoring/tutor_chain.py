from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from tutoring.prompts import GRADE_PROMPTS


def build_chain(grade):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GRADE_PROMPTS[grade]),
            ("human", "{question}"),
        ]
    )

    return prompt | llm
