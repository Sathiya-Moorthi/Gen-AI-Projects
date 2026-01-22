import json
from typing import Dict, Any
from app.services.llm_service import chat_completion

RESUME_ANALYZER_PROMPT = """You are an expert Resume Analyzer Agent for a technical interview platform.

Your job is to analyze a candidate's resume against a job description and role to:
1. Detect the candidate's seniority level (junior, mid, senior)
2. Identify key strengths relevant to the role
3. Identify skill gaps compared to the job requirements
4. Determine focus areas for the interview

Be objective and thorough in your analysis. Consider:
- Years of experience (if mentioned)
- Project complexity and scope
- Technologies and skills listed
- Leadership/mentoring experience
- Educational background

Output your analysis as a JSON object with these exact fields:
- seniority: "junior", "mid", or "senior"
- strengths: array of 3-5 key strengths
- gaps: array of 2-4 skill gaps or areas to explore
- focus_areas: array of 3-5 topics to focus on during interview

Be honest but constructive. This is for a learning-focused mock interview."""


async def analyze_resume(
    resume_text: str,
    job_description: str,
    role: str
) -> Dict[str, Any]:
    """
    Analyze resume against job description to extract insights.

    Returns:
        Dict with seniority, strengths, gaps, and focus_areas
    """
    messages = [
        {"role": "system", "content": RESUME_ANALYZER_PROMPT},
        {"role": "user", "content": f"""Analyze this resume for the role of {role}:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide your analysis as a JSON object."""}
    ]

    response = chat_completion(messages, temperature=0.3)
    content = response["content"]

    # Parse JSON from response
    try:
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        analysis = json.loads(content.strip())

        # Validate required fields
        return {
            "seniority": analysis.get("seniority", "mid").lower(),
            "strengths": analysis.get("strengths", [])[:5],
            "gaps": analysis.get("gaps", [])[:4],
            "focus_areas": analysis.get("focus_areas", [])[:5]
        }
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "seniority": "mid",
            "strengths": ["Technical skills"],
            "gaps": ["To be assessed during interview"],
            "focus_areas": ["General technical knowledge"]
        }
