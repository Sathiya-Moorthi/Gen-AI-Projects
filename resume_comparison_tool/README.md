# Resume Comparison Tool

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)

A tool to compare resumes against job descriptions using AI/NLP techniques, helping recruiters and job seekers evaluate resume-job fit.

## Project Structure

```
resume_comparison_tool/
├── scripts/
│   ├── app.py                  # Flask web application
│   ├── resume_comparison.py    # Core comparison logic
│   ├── run.py                  # Application runner
│   └── streamlit_app.py        # Streamlit interface
├── documentation/              # User guides and API docs
├── required files/             # Templates and configurations
├── output files/               # Comparison results
├── .gitignore
└── README.md
```

## Features

- Upload resume (PDF, DOCX, TXT)
- Input job description
- AI-powered similarity analysis
- Keyword matching
- Skills gap identification
- Match score calculation

## Prerequisites

- Python 3.8 or higher
- Required NLP models (downloaded on first run)

## Installation

1. Navigate to this directory:
   ```bash
   cd resume_comparison_tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Streamlit App (Recommended)
```bash
streamlit run scripts/streamlit_app.py
```

### Flask App
```bash
python scripts/run.py
```

### Programmatic Usage
```python
from scripts.resume_comparison import compare_resume

result = compare_resume(
    resume_path="path/to/resume.pdf",
    job_description="Job description text..."
)
print(f"Match Score: {result['score']}%")
```

## Input/Output Examples

### Input
- **Resume:** PDF/DOCX file containing candidate's resume
- **Job Description:** Text describing job requirements

### Output
```json
{
  "match_score": 78,
  "matched_keywords": ["python", "machine learning", "sql"],
  "missing_keywords": ["kubernetes", "aws"],
  "skills_analysis": {
    "technical": 85,
    "soft_skills": 70
  },
  "recommendations": [
    "Add cloud platform experience",
    "Highlight leadership roles"
  ]
}
```

## Configuration

Set up environment variables for AI features:
```bash
export OPENAI_API_KEY=your_api_key  # If using OpenAI
```

## Documentation

Detailed guides available in the `documentation/` folder:
- User Manual
- API Documentation
- Integration Guide

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
