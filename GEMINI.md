# 🧮 MathBuddy Architecture Notes

This file summarizes the current implementation in `app.py` and explains how the latest version works.

---

## 1. Current application flow

1. The app loads environment variables from `.env` and validates `GEMINI_API_KEY`.
2. It sets up a Google Gemini client with `genai.Client(api_key=...)`.
3. The user must sign in through Google or Microsoft OAuth before the tutor dashboard is shown.
4. Once authenticated, the app loads or creates lesson progress in `progress_data.json`.
5. The tutor uses a grade-aware system prompt and sends chat or image queries to Gemini.
6. The app keeps chat history in `StreamlitChatMessageHistory` so the conversation feels continuous.

---

## 2. Key implementation details

### Streamlit session state
`st.session_state` is used for:
- `authenticated` — whether the user has signed in
- `user_info` — profile details returned by the OAuth provider
- `current_page` — current app view
- `auth_error` — OAuth failure messaging
- `show_camera_input` — whether the camera panel is exposed
- `progress_data` — the user’s saved lesson scores

This is the main mechanism that keeps the app stateful across reruns.

### Gemini integration
The current app uses the Google Gemini SDK:
- `gemini_client.models.generate_content(...)` for text responses
- `types.Part.from_bytes(...)` for image-based math problems

The helper functions in `app.py` are:
- `history_to_gemini_contents(messages)` — converts LangChain history into Gemini content blocks
- `send_text_query_to_llm(messages, system_prompt)` — handles normal chat prompts
- `send_image_query_to_llm(image_bytes, mime_type, messages, system_prompt)` — handles uploaded or camera-captured formulas

### Grade-aware tutoring logic
The prompt is built dynamically with `get_system_prompt(grade_level)`, which switches behavior based on:
- Primary (Grades 1–5)
- Middle School (Grades 6–8)
- High School (Grades 9–12)

The system prompt instructs the model to:
- be patient and encouraging
- never reveal the final answer immediately
- ask one guiding question first
- use LaTeX-style math formatting with single dollar signs

### Progress tracking
The sidebar lets the user:
- save a score for the current lesson
- view a learning-curve chart
- download progress data as CSV

Progress is stored in `progress_data.json` under the current email address.

---

## 3. Environment variables

The app expects these values in `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MS_CLIENT_ID=your_microsoft_client_id
MS_CLIENT_SECRET=your_microsoft_client_secret
REDIRECT_URI=http://localhost:8501
```

---

## 4. How to run the project

```bash
pip install -r requirements.txt
streamlit run app.py
```

If your environment needs the module form, use:

```bash
python -m streamlit run app.py
```

---

## 5. Git workflow

Typical workflow for this repo:

```bash
git add .
git commit -m "Update tutor logic and documentation"
git push origin main
```

### What is `origin`?
`origin` is the nickname for the GitHub remote URL configured for the repository. If you move the project to a different GitHub repository, you can update it with:

```bash
git remote remove origin
git remote add origin <your-new-repo-url>
```

---

## 6. Notes for future changes

If you update the tutor behavior in `app.py`, keep these docs in sync:
- the authentication and login flow
- the Gemini model configuration
- the progress-saving logic
- the image input / vision workflow
- the grade-based tutoring prompt instructions