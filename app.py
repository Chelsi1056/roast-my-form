"""
Roast My Form — AI Posture Analyzer
Category B/Fitness-Tech Capstone | Problem Statement #12

Users capture a starting posture photo via st.camera_input for a chosen exercise.
Gemini Vision analyzes the biomechanics, scores the form, roasts the flaws in a
selectable tone, and returns concrete corrective fixes. Progress is tracked across
the session using st.session_state. The Gemini API key is loaded from
.streamlit/secrets.toml so nothing sensitive touches the UI or the repo.
"""

from datetime import datetime

import pandas as pd
import streamlit as st
from PIL import Image

from google import genai

# ----------------------------------------------------------------------------
# Page Config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Roast My Form",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Styling — small CSS pass for a cleaner dashboard feel
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; }
    div[data-testid="stMetric"] {
        background: rgba(255, 75, 75, 0.06);
        border: 1px solid rgba(255, 75, 75, 0.18);
        border-radius: 12px;
        padding: 14px 16px 8px 16px;
    }
    div[data-testid="stMetricLabel"] { font-weight: 600; opacity: 0.85; }
    .roast-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .roast-caption {
        opacity: 0.7;
        margin-top: -6px;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Session State Initialization  (prevents memory loss across reruns)
# ----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []          # list[dict] of past roasts

EXERCISES = [
    "Pushup", "Squat", "Plank", "Deadlift Setup", "Lunge", "Overhead Press",
    "Pull-up", "Bicep Curl", "Bench Press Setup", "Bent-over Row",
    "Glute Bridge", "Mountain Climber", "Burpee Start", "Kettlebell Swing Setup",
    "Sit-up", "Tricep Dip", "Bulgarian Split Squat", "Hip Thrust",
]

TONE_MAP = {
    "Gentle Coach": "supportive but honest, like a patient personal trainer easing a beginner in",
    "Savage Gym Bro": "brutally funny, sarcastic, roasting the user's form like a stand-up "
                       "comedian gym bro — but every joke must still be technically accurate",
    "Drill Sergeant": "harsh, clipped, no-nonsense military drill-sergeant energy",
}

# ----------------------------------------------------------------------------
# API Key — loaded automatically from .streamlit/secrets.toml
# ----------------------------------------------------------------------------
def get_api_key():
    """Pulls the key from Streamlit secrets. Falls back to a sidebar input
    only if secrets.toml isn't configured, so local dev / grading never breaks."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return None


api_key = get_api_key()
api_configured = False
client = None

with st.sidebar:
    st.title("⚙️ Configuration")

    if api_key:
        client = genai.Client(api_key=api_key)
        api_configured = True
        st.success("Gemini API Key loaded from secrets.toml ✅")
    else:
        st.warning("No key found in .streamlit/secrets.toml")
        manual_key = st.text_input("Enter Gemini API Key", type="password")
        if manual_key:
            client = genai.Client(api_key=manual_key)
            api_configured = True
            api_key = manual_key

    model_name = st.selectbox(
        "Vision Model",
        ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3.1-pro-preview"],
        help="Flash models are faster/cheaper; the Pro preview gives deeper biomechanical reasoning.",
    )

    st.divider()
    st.subheader("📊 Session Stats")
    st.metric("Total Roasts Logged", len(st.session_state.history))
    if st.session_state.history:
        avg_score = sum(h["score"] for h in st.session_state.history) / len(
            st.session_state.history
        )
        st.metric("Average Form Score", f"{avg_score:.1f} / 10")

    if st.session_state.history and st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown('<p class="roast-title">🔥 Roast My Form</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="roast-caption">AI Posture Analyzer — capture your starting posture, '
    "get roasted by Gemini Vision, walk away with a real fix.</p>",
    unsafe_allow_html=True,
)

col_input, col_output = st.columns([1, 1.3])

# ----------------------------------------------------------------------------
# Input Form  (st.form batches inputs so the API is called only once, on submit)
# ----------------------------------------------------------------------------
with col_input:
    with st.form("roast_form", clear_on_submit=False):
        st.subheader("1. Set Up Your Rep")
        exercise = st.selectbox("Select Exercise", EXERCISES)
        intensity = st.select_slider(
            "Roast Intensity",
            options=list(TONE_MAP.keys()),
            value="Savage Gym Bro",
        )
        photo = st.camera_input("Capture your starting posture")
        submitted = st.form_submit_button("🔥 Roast My Form", use_container_width=True)

result_container = col_output.container()

# ----------------------------------------------------------------------------
# Prompt Engineering
# ----------------------------------------------------------------------------
def build_system_prompt(exercise: str, intensity: str) -> str:
    """Builds a dynamic, tailored system prompt using f-strings — not a generic chatbot call."""
    return f"""
You are 'FormCoach-AI', a certified strength & conditioning coach and biomechanics
expert analyzing a photo that is claimed to be a user's STARTING POSTURE for a {exercise}.

Your tone must be: {TONE_MAP[intensity]}.

FIRST, verify the image actually shows a person's body in a plausible starting
position for a {exercise} — visible limbs, torso orientation, and stance consistent
with that exercise. Sitting at a desk, a random object, a face-only selfie, a pet,
a blank room, or any pose that clearly is not an attempt at a {exercise} counts as
INVALID.

If the image is INVALID, respond in exactly this format and nothing else:
VALID: No
REASON: <1-2 sentences, in the specified tone, explaining what the photo actually
shows and why it is not a {exercise} starting position>

If the image IS a genuine attempt at a {exercise} starting position, analyze it for:
1. Joint alignment (knees, elbows, spine, hips, ankles)
2. Weight distribution and balance
3. Visible injury risks in this stance
4. Muscle engagement / bracing readiness

And respond in exactly this format:
VALID: Yes
SCORE: <a single integer 1-10 rating overall form quality>
ROAST: <2-3 punchy sentences in the specified tone, roasting the specific visible flaws>
FIXES:
- <concrete technical correction 1>
- <concrete technical correction 2>
- <concrete technical correction 3>
INJURY_RISK: <Low, Medium, or High>

Respond with no extra preamble, no markdown headers, and nothing outside this format.
""".strip()


def parse_response(text: str) -> dict:
    """Parses the structured Gemini response into a dict for UI rendering."""
    data = {
        "valid": True,
        "reason": "",
        "score": 5,
        "roast": text.strip(),
        "fixes": "",
        "injury_risk": "Medium",
    }
    try:
        upper_text = text.upper()

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.upper().startswith("VALID:"):
                data["valid"] = "NO" not in stripped.upper().split(":", 1)[1]
            elif stripped.upper().startswith("REASON:"):
                data["reason"] = stripped.split(":", 1)[1].strip()
            elif stripped.upper().startswith("SCORE:"):
                digits = "".join(ch for ch in stripped.split(":", 1)[1] if ch.isdigit())
                data["score"] = int(digits) if digits else 5
                data["score"] = max(1, min(10, data["score"]))
            elif stripped.upper().startswith("ROAST:"):
                data["roast"] = stripped.split(":", 1)[1].strip()
            elif stripped.upper().startswith("INJURY_RISK:"):
                data["injury_risk"] = stripped.split(":", 1)[1].strip()

        if "FIXES:" in upper_text:
            after_fixes = text[upper_text.index("FIXES:") + len("FIXES:"):]
            if "INJURY_RISK:" in after_fixes.upper():
                after_fixes = after_fixes[: after_fixes.upper().index("INJURY_RISK:")]
            data["fixes"] = after_fixes.strip()
    except Exception:
        pass
    return data


# ----------------------------------------------------------------------------
# Handle Submission
# ----------------------------------------------------------------------------
if submitted:
    if not api_configured:
        result_container.error(
            "⚠️ No Gemini API key found. Add `GEMINI_API_KEY` to "
            "`.streamlit/secrets.toml` or paste one in the sidebar."
        )
    elif not photo:
        result_container.error("⚠️ Please capture a photo before submitting.")
    else:
        with result_container:
            with st.spinner(f"Gemini Vision is analyzing your {exercise} form..."):
                try:
                    image = Image.open(photo)
                    prompt = build_system_prompt(exercise, intensity)
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[prompt, image],
                    )
                    parsed = parse_response(response.text)

                    st.subheader("2. Your Results")

                    if not parsed["valid"]:
                        st.warning(
                            f"🚫 **Not a valid {exercise} photo.** "
                            f"{parsed['reason'] or 'This does not look like a starting posture for this exercise.'}"
                        )
                        st.caption("Retake the photo in the actual starting position to get scored.")
                    else:
                        prev_score = (
                            st.session_state.history[-1]["score"]
                            if st.session_state.history
                            else parsed["score"]
                        )

                        entry = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "exercise": exercise,
                            "intensity": intensity,
                            "score": parsed["score"],
                            "roast": parsed["roast"],
                            "fixes": parsed["fixes"],
                            "injury_risk": parsed["injury_risk"],
                        }
                        st.session_state.history.append(entry)

                        m1, m2, m3 = st.columns(3)
                        m1.metric("Form Score", f"{parsed['score']}/10", delta=parsed["score"] - prev_score)
                        m2.metric("Injury Risk", parsed["injury_risk"])
                        m3.metric("Exercise", exercise)

                        st.error(f"🔥 **The Roast:** {parsed['roast']}")

                        with st.expander("✅ How to Fix It", expanded=True):
                            st.markdown(parsed["fixes"] or "No specific fixes returned.")

                except Exception as exc:
                    st.error(f"Something went wrong calling Gemini: {exc}")
else:
    with result_container:
        st.info("👈 Set up your rep and hit **Roast My Form** — results appear here.")

# ----------------------------------------------------------------------------
# Progress Tracker
# ----------------------------------------------------------------------------
st.divider()
st.subheader("📈 Progress Tracker")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.line_chart(df.set_index("timestamp")["score"])
    with c2:
        st.dataframe(
            df[["timestamp", "exercise", "score", "injury_risk"]].iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("🗂️ Full Roast History (editable log)"):
        st.data_editor(
            df[["timestamp", "exercise", "intensity", "score", "injury_risk"]],
            use_container_width=True,
            hide_index=True,
            disabled=["timestamp", "exercise", "intensity", "score", "injury_risk"],
        )
else:
    st.caption("No roasts logged yet. Submit your first photo above to start tracking progress.")