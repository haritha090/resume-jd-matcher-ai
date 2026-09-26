# 🧩 Resume-JD Matcher AI

An AI-powered tool that compares your resume against a job description and gives
you an honest, ATS-style match score — along with the exact keywords you're
missing and concrete suggestions to improve your chances of passing screening.

Built this while actively job-hunting, to solve a real problem: manually
comparing resumes against dozens of job descriptions is slow and error-prone.

## Features

- 📄 **PDF resume parsing** — upload your resume directly, no manual copy-paste
- 🎯 **Match scoring** — 0-100 score based on realistic keyword and experience overlap
- ✅ **Matching keywords** — see what's already working in your favor
- ❌ **Missing keywords** — see exactly what the JD wants that your resume doesn't show
- 💡 **Actionable suggestions** — 3-5 specific edits to improve your match
- 🔒 **Session-only** — resume text is sent to the LLM API for analysis and is not stored anywhere

## Tech Stack

- **Frontend/UI:** Streamlit
- **PDF Parsing:** pypdf
- **LLM:** GPT-OSS 120B via the Groq API (OpenAI-compatible endpoint, so it also
  works with OpenAI's API by changing the base URL and model name)

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/haritha090/resume-jd-matcher-ai.git
   cd resume-jd-matcher-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free Groq API key**
   Sign up at [console.groq.com/keys](https://console.groq.com/keys) — the free
   tier is generous and fast (GPT-OSS 120B runs in ~1-2 seconds per request).
   
5. **Set your API key**
   ```bash
   cp .env.example .env
   # then edit .env and paste your key
   export GROQ_API_KEY=your_key_here   # macOS/Linux
   set GROQ_API_KEY=your_key_here      # Windows (cmd)
   ```

6. **Run the app**
   ```bash
   streamlit run app.py
   ```
   The app opens at `http://localhost:8501`.

## How It Works

1. You upload a resume PDF and paste a job description.
2. `pypdf` extracts the raw text from the resume.
3. Both texts are sent to GPT-OSS 120B (via Groq) with a structured prompt
   instructing it to return a strict JSON object: match score, matching
   keywords, missing keywords, and improvement suggestions.
4. The app parses that JSON and renders it as a score, keyword tags, and a
   suggestions list.

## Example Output

```json
{
  "match_score": 72,
  "matching_keywords": ["Python", "SQL", "Power BI", "Data Analysis"],
  "missing_keywords": ["REST APIs", "Git", "SDLC"],
  "suggestions": [
    "Add a line mentioning any Git/version control experience, even from coursework.",
    "Mention any REST API exposure explicitly (e.g., FastAPI) if applicable.",
    "Quantify the Power BI dashboard's business impact more prominently near the top."
  ]
}
```

## Limitations

- PDF must contain selectable text — scanned/image-based resumes won't extract correctly.
- Match scoring reflects one LLM's judgment, not a guarantee of any specific company's real ATS outcome.
- Currently supports one resume vs. one JD at a time (no batch comparison yet).

## Future Improvements

- [ ] Support DOCX resumes in addition to PDF
- [ ] Batch mode: one resume against multiple JDs at once
- [ ] Downloadable PDF report of the analysis
- [ ] Resume rewrite suggestions inline, not just keyword gaps

## Author

**Haritha Kaki** — [GitHub](https://github.com/haritha090) · [LinkedIn](https://www.linkedin.com/in/haritha-kaki-93a3a8292)
