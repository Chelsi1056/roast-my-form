# Technical Design Document — Roast My Form

## 1. Project Overview

**Project Name:** Roast My Form

**Application Type:** AI-powered fitness form analysis dashboard

**Framework:** Streamlit

**AI Model:** Google Gemini Vision

**Programming Language:** Python

Roast My Form is a multimodal AI application that analyzes a user's captured
exercise posture and provides exercise-specific technique feedback.

The application combines Streamlit's interactive UI components with Google's
Gemini multimodal AI capabilities. Users select an exercise and coaching
intensity, capture a posture image using their device camera, and submit the
image for analysis.

The system first verifies whether the image represents a valid attempt at the
selected exercise. Invalid images are rejected and are not included in the
session's progress history.

For valid exercise images, Gemini generates a form score, technique-risk
assessment, roast, detected form issues, and corrective suggestions.

> **Note:** The application provides educational fitness and technique feedback.
> It is not intended to provide medical diagnosis or professional medical
> advice.

---

# 2. Problem Statement

Incorrect exercise technique can result in inefficient movement and poor
training habits.

Traditional fitness applications often provide generic exercise instructions,
but they do not provide personalized feedback based on the user's actual
posture.

Roast My Form addresses this problem by allowing users to submit a camera image
of their exercise posture and receive AI-generated, exercise-specific feedback.

The application combines technical feedback with an adjustable humorous
coaching style to make the experience more engaging.

---

# 3. Project Objectives

The primary objectives of the system are:

1. Build an interactive Streamlit fitness-analysis application.
2. Integrate Gemini's multimodal vision capabilities.
3. Accept camera images directly through the browser.
4. Validate whether the submitted image matches the selected exercise.
5. Generate exercise-specific form feedback.
6. Provide adjustable AI coaching and roast intensity.
7. Maintain a session-based history of valid analyses.
8. Visualize form-score progress.
9. Demonstrate secure API-key management.
10. Deploy the application to a cloud platform.

---

# 4. Functional Requirements

## 4.1 Exercise Selection

The user can select an exercise from the supported exercise list.

The application currently supports 18 exercises:

- Pushup
- Squat
- Plank
- Deadlift Setup
- Lunge
- Overhead Press
- Pull-up
- Bicep Curl
- Bench Press Setup
- Bent-over Row
- Glute Bridge
- Mountain Climber
- Burpee Start
- Kettlebell Swing Setup
- Sit-up
- Tricep Dip
- Bulgarian Split Squat
- Hip Thrust

---

## 4.2 Roast Intensity

The user can select the desired coaching tone.

The AI adapts its response based on the selected intensity, ranging from a
gentle coaching style to a more aggressive humorous roast.

The roast affects the presentation style while the technical analysis remains
focused on exercise form.

---

## 4.3 Camera Input

The application uses Streamlit's:

```python
st.camera_input()
```

to capture an image directly from the user's browser or device camera.

The captured image is passed to the AI analysis pipeline.

---

## 4.4 Form Submission

The application groups the user's exercise selection, roast intensity, and
camera input inside a Streamlit form.

The form ensures that the Gemini API is called only when the user explicitly
submits the analysis request.

The workflow is:

```text
Exercise Selection
        +
Roast Intensity
        +
Camera Image
        ↓
Form Submission
        ↓
AI Analysis
```

---

## 4.5 Image Validation

Before generating a form score, the application verifies whether the submitted
image represents the selected exercise.

The AI checks whether:

- The selected exercise is visible.
- A suitable body posture is present.
- The image represents a genuine attempt at the selected exercise.
- The image is not an unrelated object or photograph.

The validation produces either:

```text
VALID: Yes
```

or:

```text
VALID: No
```

If the image is invalid, the application displays a warning and the submission
is not added to the session history.

---

## 4.6 Form Analysis

For a valid exercise image, Gemini analyzes the visible posture and generates
exercise-specific feedback.

The analysis includes:

- Form score
- Technique/injury risk assessment
- AI-generated roast
- Detected form issues
- Corrective suggestions

The result is then displayed through the Streamlit dashboard.

---

## 4.7 Progress Tracking

Valid analyses are stored in:

```python
st.session_state.history
```

The stored records are used to generate:

- Form-score trends
- Score deltas
- Session history
- Editable analysis records

Invalid images are excluded from the history so that they do not affect the
progress calculations.

---

# 5. Non-Functional Requirements

## 5.1 Usability

The application provides a simple workflow:

```text
Select Exercise
       ↓
Select Roast Intensity
       ↓
Capture Image
       ↓
Submit
       ↓
Receive Feedback
```

The interface is designed so that the user can complete an analysis without
requiring technical knowledge.

---

## 5.2 Performance

The application minimizes unnecessary Gemini API requests by using a
form-based submission workflow.

Changing the exercise or roast intensity does not trigger an AI request.
The Gemini API is called only when the user submits the form.

---

## 5.3 Reliability

The application handles common failure conditions including:

- Missing API key
- Missing camera image
- Invalid exercise image
- Gemini API errors
- Unexpected AI responses

The application displays appropriate error or warning messages instead of
terminating the entire Streamlit application.

---

## 5.4 Security

The Gemini API key is not hardcoded into the source code.

During local development, the key is stored using:

```text
.streamlit/secrets.toml
```

During cloud deployment, the key is configured using the deployment platform's
secret-management system.

The real API key must never be committed to GitHub.

---

# 6. System Architecture

The application follows a layered architecture consisting of the user
interface, input validation, prompt generation, Gemini inference, response
parsing, session-state management, and presentation layers.

```text
User
  ↓
Streamlit UI
  ↓
Exercise + Roast Intensity + Camera Image
  ↓
Form Submission
  ↓
Input Validation
  ↓
Dynamic Prompt
  ↓
Gemini Vision API
  ↓
Response Parsing
  ↓
Validity Check
  ├── Invalid → Warning + Retake Request
  │
  └── Valid
        ↓
   Form Analysis
        ↓
   Session State
        ↓
   Dashboard
        ↓
   Progress Tracker
```

---

# 7. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend / UI | Streamlit |
| AI Engine | Google Gemini Vision |
| Gemini SDK | `google-genai` |
| Data Processing | Pandas |
| Image Processing | Pillow |
| State Management | Streamlit Session State |
| Visualization | Streamlit Charts |
| Version Control | Git / GitHub |
| Deployment | Streamlit Community Cloud |

---

# 8. Gemini API Integration

The application uses the Google GenAI Python SDK:

```python
from google import genai
```

The Gemini client is initialized using the configured API key:

```python
client = genai.Client(api_key=api_key)
```

The application sends both the dynamic text prompt and captured image to the
Gemini model.

Conceptually:

```python
response = client.models.generate_content(
    model=model_name,
    contents=[prompt, image]
)
```

This is a multimodal request because Gemini receives both textual instructions
and visual information.

---

# 9. Prompt Engineering

Prompt engineering is a core component of Roast My Form.

The application dynamically constructs the prompt based on the user's selected
exercise and roast intensity.

Conceptually:

```python
prompt = f"""
Analyze the user's starting posture.

Selected exercise:
{exercise}

Coaching intensity:
{intensity}
"""
```

The prompt instructs Gemini to:

1. Verify the selected exercise.
2. Determine whether the image is a valid exercise attempt.
3. Reject unrelated or unsuitable images.
4. Analyze form only when the image is valid.
5. Generate structured feedback.
6. Adapt the response tone according to the selected intensity.

This allows the AI to behave as an exercise-specific coaching engine rather than
a generic chatbot.

---

# 10. Validity-Gated AI Pipeline

A major design feature of the application is the validity check performed
before assigning a form score.

The AI first determines:

```text
VALID: Yes
```

or:

```text
VALID: No
```

### Invalid Image

If the image is invalid:

```text
Invalid Image
      ↓
Warning
      ↓
Reason
      ↓
Retake Photo
```

The application does not generate a form score and does not add the submission
to the session history.

### Valid Image

If the image is valid:

```text
VALID
  ↓
SCORE
  ↓
ROAST
  ↓
FIXES
  ↓
INJURY_RISK
```

The structured result is then displayed in the dashboard.

---

# 11. Response Parsing

Gemini is instructed to return a predictable response format.

The application extracts fields such as:

```text
VALID
REASON
SCORE
ROAST
FIXES
INJURY_RISK
```

The response parser converts the AI-generated text into structured values that
can be used by the Streamlit interface.

The processing flow is:

```text
Gemini Response
      ↓
parse_response()
      ↓
Structured Python Data
      ↓
Streamlit Dashboard
```

This separates AI inference from UI rendering and makes the application easier
to maintain.

---

# 12. Session State Management

Streamlit reruns the application when users interact with widgets.

To preserve analysis history during these reruns, the application uses:

```python
st.session_state.history
```

The history contains valid analysis records.

Example:

```python
{
    "timestamp": "2026-08-12 10:03:00",
    "exercise": "Squat",
    "intensity": "Savage Gym Bro",
    "score": 4,
    "roast": "...",
    "fixes": "...",
    "injury_risk": "Medium"
}
```

This history is used by the dashboard to display:

- Current score
- Score delta
- Progress trend
- Analysis history

Invalid submissions are not stored.

---

# 13. Data Flow

The complete application data flow is:

```text
User
 ↓
Streamlit Interface
 ↓
Exercise + Intensity + Camera Image
 ↓
Form Submission
 ↓
Input Validation
 ↓
Dynamic Prompt Construction
 ↓
Gemini Vision API
 ↓
AI Response
 ↓
Validity Check
 ├───────────────┐
 │               │
Invalid         Valid
 │               │
Warning          Parse Response
 │               │
No History      Session State
                 │
                 ↓
              Dashboard
                 │
          ┌──────┴──────┐
          ↓             ↓
       Current       Historical
       Results        Results
```

---

# 14. UI and Visualization Design

The application uses Streamlit components to create an interactive dashboard.

## Input Components

The input section includes:

- Exercise selector
- Roast intensity selector
- Camera input
- Submit button

## KPI Components

The application uses:

```python
st.metric()
```

to display key information such as:

- Form score
- Score change
- Technique risk

## Feedback Components

The application uses:

```python
st.error()
```

for prominent feedback and:

```python
st.expander()
```

for detailed corrections.

Invalid images are displayed using:

```python
st.warning()
```

## Progress Components

The application uses:

```python
st.line_chart()
```

to display form-score progress.

The analysis history is displayed using:

```python
st.data_editor()
```

---

# 15. API Call Optimization

The application uses a form-based interaction model to reduce unnecessary
Gemini API calls.

The workflow is:

```text
User changes settings
        ↓
No Gemini request
        ↓
User clicks Submit
        ↓
One Gemini request
        ↓
Display result
```

This helps reduce unnecessary API usage and prevents repeated analysis during
normal UI interaction.

---

# 16. Error Handling

The application handles several possible failure scenarios.

## Missing API Key

If the Gemini API key is unavailable, the application displays an error and
provides the appropriate configuration option.

## Missing Photo

If the user submits the form without a camera image, the application displays
an error and requests a photo.

## Invalid Photo

If the captured image does not match the selected exercise, the application
displays a warning and does not create a history entry.

## Gemini API Error

If the Gemini API request fails, the application catches the error and displays
an appropriate Streamlit error message.

## Unexpected AI Response

If the AI response does not follow the expected format, the application
handles the parsing failure without crashing the entire dashboard.

---

# 17. Security Design

The Gemini API key is treated as sensitive configuration data.

## Local Development

The key is stored in:

```text
.streamlit/secrets.toml
```

Example:

```toml
GEMINI_API_KEY = "your-key-here"
```

## GitHub

The real secrets file is excluded through `.gitignore`.

A template can be included:

```text
.streamlit/secrets.toml.example
```

containing:

```toml
GEMINI_API_KEY = "your-key-here"
```

## Cloud Deployment

The production API key is configured through Streamlit Community Cloud's
secret-management interface.

The API key is never hardcoded into `app.py` or committed to the repository.

---

# 18. Deployment Design

The intended deployment architecture is:

```text
GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
Install requirements.txt
       ↓
Run app.py
       ↓
Load Cloud Secrets
       ↓
Connect to Gemini API
       ↓
Live Streamlit Application
```

The GitHub repository contains the application source code and dependency
configuration, while the Gemini API key remains securely stored as a deployment
secret.

---

# 19. Repository Structure

```text
roast-my-form/
│
├── .streamlit/
│   ├── secrets.toml
│   └── secrets.toml.example
│
├── .gitignore
├── app.py
├── architecture.md
├── README.md
├── requirements.txt
└── technical_design.md
```

The real `secrets.toml` file is local-only and must never be committed to
GitHub.

---

# 20. Testing Strategy

The application should be tested using different input scenarios.

## Test Case 1 — Valid Exercise Image

**Input:** A suitable squat posture while Squat is selected.

**Expected Result:**

- Image is accepted.
- Form score is generated.
- Roast is generated.
- Corrections are generated.
- Risk is displayed.
- Result is added to history.

---

## Test Case 2 — Wrong Exercise

**Input:** A pushup image while Squat is selected.

**Expected Result:**

- Image is rejected.
- Reason is displayed.
- No score is generated.
- No history entry is created.

---

## Test Case 3 — Random Image

**Input:** An unrelated object or photograph.

**Expected Result:**

- Image is rejected.
- Invalid-photo warning is displayed.
- No score is generated.
- No history entry is created.

---

## Test Case 4 — Missing Image

**Input:** Exercise and intensity selected without a camera image.

**Expected Result:**

- Validation error is displayed.
- Gemini request is not made.

---

## Test Case 5 — Missing API Configuration

**Input:** Gemini API key unavailable.

**Expected Result:**

- Configuration error is displayed.
- The application does not make an invalid API request.

---

## Test Case 6 — Multiple Valid Submissions

**Input:** Several valid exercise images.

**Expected Result:**

- Each valid result is stored in session history.
- Score trend updates.
- KPI delta updates.
- Data editor displays the accumulated records.

---

# 21. Current Limitations

The current version analyzes a captured posture image rather than continuous
exercise video.

Therefore, it does not currently perform:

- Real-time joint tracking
- Full repetition counting
- Frame-by-frame movement analysis
- Continuous video feedback
- Persistent user profiles
- Long-term database-backed progress tracking

The quality of the analysis can also depend on:

- Image quality
- Camera angle
- Lighting
- Body visibility
- Selected exercise
- Gemini model capabilities

The application should therefore be treated as an educational fitness
technique tool rather than a medical diagnostic system.

---

# 22. Future Enhancements

Potential future improvements include:

1. Multi-frame exercise analysis.
2. Full repetition tracking.
3. Real-time pose estimation.
4. Joint-angle measurement.
5. Audio coaching feedback.
6. Persistent user accounts.
7. Long-term progress analytics.
8. Downloadable PDF reports.
9. Exercise-specific performance dashboards.
10. Integration with wearable fitness data.

---

# 23. Conclusion

Roast My Form demonstrates the integration of Streamlit, Python, multimodal
generative AI, image processing, session-state management, and interactive
visualization in a real-world application.

The validity-gated architecture ensures that irrelevant images are rejected
before form scores are generated, while session-state management allows valid
analyses to be tracked throughout the user's session.

The project demonstrates practical implementation of:

- Streamlit forms
- Camera input
- Gemini multimodal AI
- Dynamic prompt engineering
- Structured AI response parsing
- Session state
- KPI dashboards
- Data visualization
- Secure API-key management
- Cloud deployment architecture