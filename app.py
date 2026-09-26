"""
Resume-JD Matcher AI
--------------------
A Streamlit app that takes a resume (PDF) and a job description (text),
then uses an LLM (via the Groq API, OpenAI-compatible) to:
  1. Score the match between the resume and the JD (0-100)
  2. List the skills/keywords already matching
  3. List important keywords missing from the resume
  4. Give 3-5 concrete suggestions to improve the match

Run locally with:
    streamlit run app.py
"""

import json
import os

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Groq gives a generous free tier and is OpenAI-API compatible, so the same
# `openai` client library works by just pointing base_url at Groq's endpoint.
# Get a free key at https://console.groq.com/keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "openai/gpt-oss-120b"

st.set_page_config(page_title="Resume-JD Matcher AI", page_icon="🧩", layout="wide")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def extract_text_from_pdf(uploaded_file) -> str:
    """Extract raw text from an uploaded PDF file object."""
    reader = PdfReader(uploaded_file)
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_parts).strip()


def build_prompt(resume_text: str, jd_text: str) -> str:
    """Build the instruction prompt sent to the LLM."""
    return f"""
You are an expert technical recruiter and ATS (Applicant Tracking System) analyst.
Compare the RESUME below against the JOB DESCRIPTION and evaluate the match.

Respond with ONLY a valid JSON object (no markdown fences, no extra text) in
exactly this shape:

{{
  "match_score": <integer 0-100>,
  "matching_keywords": [<list of skills/keywords found in BOTH resume and JD>],
  "missing_keywords": [<list of important JD keywords NOT found in the resume>],
  "suggestions": [<3 to 5 short, specific, actionable suggestions to improve the match>]
}}

Rules:
- match_score should reflect realistic ATS-style keyword and experience overlap,
  not just general impression. Be honest, not generous.
- Do not invent skills the resume doesn't support.
- Keep each suggestion to one sentence.

RESUME:
\"\"\"{resume_text}\"\"\"

JOB DESCRIPTION:
\"\"\"{jd_text}\"\"\"
"""


def get_match_analysis(resume_text: str, jd_text: str) -> dict:
    """Call the LLM and return the parsed JSON analysis."""
    client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": build_prompt(resume_text, jd_text)}],
        temperature=0.2,
    )

    raw_output = response.choices[0].message.content.strip()

    # The model occasionally wraps JSON in ```json fences despite instructions —
    # strip those defensively before parsing.
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json\n", "", 1)

    return json.loads(raw_output)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
st.title("🧩 Resume-JD Matcher AI")
st.caption(
    "Upload your resume and paste a job description to get an honest, "
    "ATS-style match score with concrete improvement suggestions."
)

if not GROQ_API_KEY:
    st.warning(
        "No GROQ_API_KEY found in environment variables. "
        "Set it before running (see README.md) or the analysis step will fail.",
        icon="⚠️",
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload your resume (PDF)")
    resume_file = st.file_uploader("Resume PDF", type=["pdf"], label_visibility="collapsed")

with col2:
    st.subheader("2. Paste the job description")
    jd_text_input = st.text_area(
        "Job description", height=280, label_visibility="collapsed",
        placeholder="Paste the full job description here...",
    )

analyze_clicked = st.button("🔍 Analyze Match", type="primary", use_container_width=True)

if analyze_clicked:
    if not resume_file:
        st.error("Please upload a resume PDF first.")
    elif not jd_text_input.strip():
        st.error("Please paste a job description first.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY is not set. See README.md for setup instructions.")
    else:
        with st.spinner("Reading resume and calling the AI model..."):
            try:
                resume_text = extract_text_from_pdf(resume_file)
                if not resume_text:
                    st.error(
                        "Couldn't extract any text from that PDF. "
                        "It may be a scanned image — try a text-based PDF instead."
                    )
                    st.stop()

                result = get_match_analysis(resume_text, jd_text_input)
            except json.JSONDecodeError:
                st.error("The AI response wasn't valid JSON. Please try again.")
                st.stop()
            except Exception as exc:  # noqa: BLE001 - surfaced directly to the user
                st.error(f"Something went wrong: {exc}")
                st.stop()

        # ---------------- Results ----------------
        st.divider()
        score = result.get("match_score", 0)

        score_col, _ = st.columns([1, 2])
        with score_col:
            st.metric("Match Score", f"{score}/100")
            st.progress(min(max(score, 0), 100) / 100)

        matched_col, missing_col = st.columns(2)

        with matched_col:
            st.subheader("✅ Matching Keywords")
            matching = result.get("matching_keywords", [])
            if matching:
                st.write(" ".join(f"`{kw}`" for kw in matching))
            else:
                st.write("None detected.")

        with missing_col:
            st.subheader("❌ Missing Keywords")
            missing = result.get("missing_keywords", [])
            if missing:
                st.write(" ".join(f"`{kw}`" for kw in missing))
            else:
                st.write("None — great coverage!")

        st.subheader("💡 Suggestions to Improve Your Match")
        for i, suggestion in enumerate(result.get("suggestions", []), start=1):
            st.write(f"{i}. {suggestion}")

st.divider()
st.caption("Built with Streamlit + Groq (Llama 3.3 70B) · Resume text never leaves this session.")
