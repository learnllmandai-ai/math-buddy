import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MathBuddy K-12", page_icon="🧮", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 MathBuddy Login")
    st.write("Welcome! Please sign in to access your math tutor.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login with Google", use_container_width=True):
            # In a production environment, you would implement OAuth2 logic here
            st.session_state["authenticated"] = True
            st.rerun()
            
    with col2:
        if st.button("Login with Microsoft", use_container_width=True):
            # In a production environment, you would implement OAuth2 logic here
            st.session_state["authenticated"] = True
            st.rerun()
    st.stop()

st.title("🧮 MathBuddy: Your K-12 Math Tutor")
st.write("Ask me any math question from Grade 1 to 12. Let's learn together!")

with st.sidebar:
    st.header("Account")
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["messages"] = [] # Clear history on logout
        st.rerun()

SYSTEM_PROMPT = """You are 'MathBuddy', a patient, enthusiastic, and friendly math tutor for students from Grades 1 to 12. 
- Adapt your tone to the student's grade level. Use emojis/analogies for lower grades, clear logic for middle school, and rigorous math terminology (using LaTeX format like $x^2$) for high school.
- NEVER give the final answer immediately. Break problems down and ask guiding questions to help the student find the answer themselves.
- If they make a mistake, be incredibly encouraging!"""

if "messages" not in st.session_state:
    st.session_state["messages"] = [SystemMessage(content=SYSTEM_PROMPT)]

for message in st.session_state["messages"]:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant", avatar="🧮"):
            st.write(message.content)

if user_query := st.chat_input("How can I help you with math today?"):
    with st.chat_message("user"):
        st.write(user_query)
    st.session_state["messages"].append(HumanMessage(content=user_query))

    with st.chat_message("assistant", avatar="🧮"):
        with st.spinner("Thinking..."):
            try:
                llm = ChatOpenAI(
                    model="gpt-4o",
                    temperature=0.2
                )
                response = llm.invoke(st.session_state["messages"])
                st.write(response.content)
                st.session_state["messages"].append(AIMessage(content=response.content))
            except Exception as e:
                st.error(f"An error occurred: {e}")