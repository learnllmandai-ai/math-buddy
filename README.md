# 🧮 MathBuddy: K-12 Math Tutor

MathBuddy is an AI-powered math tutoring application designed for students from Grade 1 to 12. Built with Streamlit and LangChain, it provides a patient, encouraging, and adaptive learning experience.

## ✨ Features

- **Adaptive Tutoring:** Adjusts tone, emojis, and complexity based on the student's grade level.
- **Step-by-Step Guidance:** Follows a pedagogical approach—never giving the final answer immediately, but guiding the student to discover it.
- **LaTeX Support:** Beautifully renders mathematical formulas (e.g., $x^2 + y^2 = r^2$) for clarity.
- **Authentication:** Includes a secure-entry UI with Google and Microsoft login options.
- **Conversation Memory:** Remembers previous context within a session to provide continuous support.

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)
- **AI Framework:** [LangChain](https://www.langchain.com/)
- **LLM:** OpenAI GPT-4o
- **Environment Management:** `python-dotenv`

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Varsid
   ```

2. **Install dependencies:**
   ```bash
   pip install streamlit langchain-openai python-dotenv requests pandas
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   GOOGLE_CLIENT_ID=your_google_id
   GOOGLE_CLIENT_SECRET=your_google_secret
   MS_CLIENT_ID=your_ms_id
   MS_CLIENT_SECRET=your_ms_secret
   REDIRECT_URI=http://localhost:8501
   ```

### Running the Application

```bash
python -m streamlit run app.py
```

## 📝 Documentation
For detailed technical architecture notes and Git workflows, please see GEMINI.md.
