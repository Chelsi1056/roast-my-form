# 🔥 roast-my-form

```
$ whoami
> AI Biomechanics Coach powered by Gemini Vision

$ ./roast_my_form.sh --exercise squat --intensity savage
[INFO] Booting FormCoach-AI...
[INFO] Loading GEMINI_API_KEY from .streamlit/secrets.toml...
[INFO] Camera stream initialized...
[INFO] Frame captured. Sending to gemini-3.6-flash...
[CHECK] Image validity: PASS — starting posture matches squat
[WARN] Knee valgus detected on frame 1.
[WARN] Anterior pelvic tilt: MODERATE.
[ROAST] "Your knees are caving in like a bad Wi-Fi signal. Fix it before you fix nothing else."
[OK] Score: 4/10 | Injury Risk: Medium
$ _
```

> Point a camera at your starting posture. Get roasted. Get corrected. Get stronger.

---

## 📦 What This Is

**Roast My Form** is a Streamlit app that uses **Gemini Vision** multimodality to
analyze a photo of your exercise starting posture and returns:

- A **validity check** — flags photos that don't actually match the selected
  exercise (wrong pose, no body visible, random object) instead of scoring them
- A **Form Score** (1–10) for genuine attempts
- A tone-selectable **roast** of your biomechanical flaws (Gentle Coach → Drill Sergeant)
- Concrete, technical **fixes**
- An **Injury Risk** rating
- A running **progress tracker** across your session

Supports 18 exercises: Pushup, Squat, Plank, Deadlift Setup, Lunge, Overhead
Press, Pull-up, Bicep Curl, Bench Press Setup, Bent-over Row, Glute Bridge,
Mountain Climber, Burpee Start, Kettlebell Swing Setup, Sit-up, Tricep Dip,
Bulgarian Split Squat, Hip Thrust.

---

## 🖥️ Tech Stack

| Layer          | Tool                                  |
|----------------|----------------------------------------|
| Frontend / UI  | Streamlit (`st.camera_input`, `st.form`, `st.metric`, `st.data_editor`) |
| AI Engine      | Gemini Vision (`google-genai`, the current unified Google GenAI SDK) |
| Data Handling  | Pandas                                |
| Image Handling | Pillow                                |
| Secrets        | `.streamlit/secrets.toml` (auto-loaded, never committed) |
| Deployment     | Streamlit Community Cloud / HF Spaces / Render |

> **Note:** the older `google-generativeai` package is deprecated and fully
> shut down. This project uses its replacement, `google-genai`
> (`from google import genai`, `genai.Client(...)`).

---

## 🚀 Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/roast-my-form.git
cd roast-my-form

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your real key

# 5. Run it
python3 -m streamlit run app.py
```

Grab a free Gemini API key at
[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
Once `secrets.toml` has it, the sidebar shows a green "loaded ✅" automatically
— no need to paste the key into the UI every session.

---

## 🔐 Secrets & Deployment

`GEMINI_API_KEY` lives in `.streamlit/secrets.toml`, which is git-ignored by
default (see `.gitignore`). Never commit your real key — commit
`.streamlit/secrets.toml.example` instead, so collaborators know the expected
format.

On **Streamlit Community Cloud**, set the same key under
`Settings → Secrets`:

```toml
GEMINI_API_KEY = "your-key-here"
```

If no key is found anywhere, the app falls back to a manual password field in
the sidebar so local dev and grading never hard-break.

---

## 🧠 How It Works (Short Version)

1. User selects an exercise + roast intensity inside an `st.form` — this batches
   all inputs so **one submit = one API call** (no wasted quota on every rerun).
2. `st.camera_input` captures the posture photo directly in-browser.
3. A dynamically built **system prompt** (via f-strings) first asks Gemini
   Vision to verify the photo is a genuine attempt at the selected exercise's
   starting posture. Mismatched photos (wrong pose, no visible body, random
   objects) are rejected with a reason instead of being scored.
4. Valid photos are analyzed for joint alignment, balance, injury risk, and
   engagement, and Gemini returns a strict, parseable format.
5. The response is parsed into `VALID`, `SCORE`, `ROAST`, `FIXES`, `INJURY_RISK`
   and rendered as KPI cards + an expander — or a "not a valid photo" warning.
6. Only valid, scored submissions are appended to `st.session_state.history`,
   powering the `st.line_chart` progress tracker and `st.data_editor` log —
   no data lost on rerun, and no invalid attempts skewing your average score.

See [`architecture.md`](./architecture.md) for the full system design and data flow diagram.

---

## 🌐 Live Demo

🔗 **[your-deployed-app-url-here]**

---

## 📁 Repo Structure

```
roast-my-form/
├── .streamlit/         
│   └── secrets.toml.example    # Template committed to the repo
├── .gitignore
├── app.py                      # Main Streamlit application
├── requirements.txt            # Pinned dependencies
├── README.md                   # You are here
└── architecture.md             # System design & data flow
```

---

## 🏋️ Roadmap / Ideas

- [ ] Multi-frame video analysis (full rep, not just starting posture)
- [ ] Export session history as a downloadable PDF report
- [ ] Rep-over-time trend comparison across multiple exercises
- [ ] Audio coaching cues via text-to-speech

---

## 📄 License

MIT — fork it, roast it, improve it.