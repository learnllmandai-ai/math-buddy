# 🧮 MathBuddy: Gemini-Powered K-12 Math Tutor

MathBuddy is a Streamlit-based AI tutor for students in Grades 1–12. The current app uses Google Gemini for tutoring, supports Google and Microsoft OAuth sign-in, tracks lesson progress, and can solve handwritten math images with Gemini Vision.

## ✨ What the app does now

- **Adaptive tutoring:** Uses the selected grade band to tailor the tone, explanation level, and examples.
- **Step-by-step guidance:** Encourages students to think first rather than immediately revealing the answer.
- **Gemini AI support:** Uses Google Gemini for chat responses and image-based math help.
- **Handwritten formula input:** Lets users upload or capture a photo of a math problem and send it to Gemini Vision.
- **OAuth login:** Supports Google sign-in and Microsoft sign-in through the configured OAuth flow.
- **Progress tracking:** Saves lesson scores to `progress_data.json` and shows a simple learning-curve chart in the sidebar.
- **Session memory:** Keeps the current chat history during the active session.
- **Knowledge mastery tracking:** Planned analytics for topic-level mastery and learning growth.
- **Adaptive difficulty:** Planned difficulty switching based on mastery percentage.
- **Misconception detection:** Planned error-pattern analysis for common math mistakes.
- **Gamification:** Planned XP, badges, and streak tracking to increase engagement.
- **Voice tutoring:** Planned speech-to-text and text-to-speech support.
- **OCR worksheet solving:** Planned worksheet image analysis for math practice.
- **Teacher and parent dashboards:** Planned reporting for classroom and home progress.
- **Multilingual support:** Planned English and Tamil tutoring prompts.

## 🛠️ Current tech stack

- **Frontend/UI:** Streamlit
- **AI model:** Google Gemini (`google-genai`)
- **Conversation history:** LangChain message objects and `StreamlitChatMessageHistory`
- **Utilities:** Python, `requests`, `pandas`, `python-dotenv`

## 🚀 Getting started

### Prerequisites

- Python 3.10+
- A Gemini API key from Google AI Studio
- Optional OAuth credentials for Google and/or Microsoft sign-in

### Installation

1. Clone the repository and enter the project folder.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with the following variables:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-2.5-flash
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   MS_CLIENT_ID=your_microsoft_client_id
   MS_CLIENT_SECRET=your_microsoft_client_secret
   REDIRECT_URI=http://localhost:8501
   ```

   Notes:
   - `GEMINI_API_KEY` is required for the tutor to work.
   - Google sign-in requires `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`.
   - Microsoft sign-in is optional and uses `MS_CLIENT_ID` and `MS_CLIENT_SECRET`.

### Run the app

```bash
streamlit run app.py
```

You can also use:

```bash
python -m streamlit run app.py
```

## 🧩 Feature modules

- `tutoring/adaptive_engine.py` — adaptive difficulty logic
- `tutoring/misconception_detector.py` — misconception and error-pattern analysis
- `gamification/xp_manager.py`, `badge_engine.py`, `streak_tracker.py` — engagement and rewards
- `analytics/mastery_tracker.py`, `reports.py` — mastery and reporting
- `dashboards/teacher_dashboard.py`, `parent_dashboard.py` — classroom and parent views
- `multilingual/translator.py`, `language_prompts.py` — English/Tamil support
- `voice/speech_to_text.py`, `text_to_speech.py` — voice input and output
- `vision/worksheet_ocr.py`, `image_preprocessor.py` — worksheet OCR and image preparation

## 📁 Important files

- `app.py` — main Streamlit application
- `progress_data.json` — stores lesson scores for the logged-in user
- `GEMINI.md` — technical notes and architecture overview

## 📝 Documentation

For the current implementation details, prompt logic, Gemini integration, and project notes, see [GEMINI.md](GEMINI.md).