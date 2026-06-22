# 🧮 MathBuddy Architecture Notes

This file summarizes the current implementation in `app.py` and the expanded roadmap for the next phase of the project.

---

## 1. Current application flow

1. The app loads environment variables from `.env` and validates `GEMINI_API_KEY`.
2. It sets up a Google Gemini client with `genai.Client(api_key=...)`.
3. **Pre-loader:** A high-quality CSS/HTML animation initializes the "ABACUS ELITE" branding.
4. **Authentication:** The user must sign in through Google or Microsoft OAuth.
5. **Dashboard:**
   - **Interactive Abacus:** A custom CSS-driven Soroban abacus for manual practice.
   - **Adaptive Tutoring:** Uses a mastery-based engine to adjust difficulty and detect misconceptions.
   - **Multimodal Input:** Supports text chat and "Snap & Solve" vision for handwritten formulas.
   - **Native Voice:** Gemini-powered TTS for auditory learning.
6. **Persistence:** Chat history and session stats (XP, Streaks) are maintained in `st.session_state`.

---

## 2. Expanded feature roadmap

The current project structure now includes the following enhancement areas:

- `tutoring/adaptive_engine.py` for mastery-based difficulty switching
- `tutoring/misconception_detector.py` for error-pattern analysis
- `gamification/xp_manager.py`, `badge_engine.py`, and `streak_tracker.py` for learner engagement
- `analytics/mastery_tracker.py` and `reports.py` for learning progress analysis
- `dashboards/teacher_dashboard.py` and `parent_dashboard.py` for reporting
- `multilingual/translator.py` and `language_prompts.py` for English/Tamil support
- `voice/speech_to_text.py` and `text_to_speech.py` for voice tutoring
- `vision/worksheet_ocr.py` and `image_preprocessor.py` for OCR-based worksheet solving

### Recommended development order

Phase 1 (must have):
1. Knowledge mastery tracking
2. Adaptive difficulty
3. Misconception detection

Phase 2:
1. Gamification
2. OCR worksheet solver
3. Multi-language support

Phase 3:
1. Voice tutoring
2. Teacher dashboard
3. Parent reports

## 3. Key implementation details

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
The system uses `tutoring/tutor_chain.py` to build LangChain-based reasoning chains, switching behavior based on:
- Primary (Grades 1–5)
- Middle School (Grades 6–8)
- High School (Grades 9–12)

### Advanced Features
1. **Pedagogy Enforcement:** Intercepts student requests for "just the answer" to encourage step-by-step thinking.
2. **Mastery Analytics:** Implements an Exponential Moving Average (EMA) to track progress across topics like Algebra, Geometry, and Fractions.
3. **Misconception Detection:** Scans user input for specific error patterns to provide targeted hints.
4. **Gamification:** Integrated XP, Streaks, and Badges to drive student retention.
5. **Multilingual Support:** Dynamic translation for Tamil (தமிழ்) and English.

### Progress tracking
The sidebar lets the user:
- save a score for the current lesson
- view a learning-curve chart
- download progress data as CSV

Progress is stored in `progress_data.json` under the current email address.

---

## 4. Environment variables

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

## 5. How to run the project

```bash
pip install -r requirements.txt
streamlit run app.py
```

If your environment needs the module form, use:

```bash
python -m streamlit run app.py
```

---

## 6. Git workflow

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

## 7. Feature implementation notes

The following feature areas are now part of the project plan and are reflected in the starter module structure:

- **XP, badges, streaks:** `gamification/xp_manager.py`, `badge_engine.py`, `streak_tracker.py`
- **Knowledge mastery:** `analytics/mastery_tracker.py` and `reports.py`
- **Adaptive difficulty:** `tutoring/adaptive_engine.py`
- **Misconception detection:** `tutoring/misconception_detector.py`
- **Voice tutoring:** `voice/speech_to_text.py`, `text_to_speech.py`
- **OCR worksheet solving:** `vision/worksheet_ocr.py`, `image_preprocessor.py`
- **Teacher and parent dashboards:** `dashboards/teacher_dashboard.py`, `parent_dashboard.py`
- **Multilingual tutoring:** `multilingual/translator.py`, `language_prompts.py`

Recommended priorities:
1. mastery tracking
2. adaptive difficulty
3. misconception detection
4. gamification and OCR
5. voice and multilingual dashboards

## 8. Notes for future changes

If you update the tutor behavior in `app.py`, keep these docs in sync:
- the authentication and login flow
- the Gemini model configuration
- the progress-saving logic
- the image input / vision workflow
- the grade-based tutoring prompt instructions