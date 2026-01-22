import json
from typing import Dict, Any, List
from app.services.llm_service import chat_completion

FEEDBACK_AGENT_PROMPT = """You are an expert Interview Feedback Agent.

Your role is to generate comprehensive, constructive feedback reports after an interview.

Your feedback must include:
1. Overall Assessment - Brief summary of performance
2. Scoring Summary - Technical, Design, Communication scores explained
3. Key Strengths - What the candidate did well
4. Areas for Improvement - Constructive feedback on gaps
5. Hiring Recommendation - Hire / Borderline / No-Hire with justification
6. Skill Roadmap - Specific learning recommendations

TONE GUIDELINES:
- Be honest but encouraging
- Focus on growth potential
- Provide actionable feedback
- Acknowledge effort and good attempts
- Frame weaknesses as learning opportunities

RECOMMENDATION CRITERIA:
- Hire: Meets or exceeds expectations for the role and seniority
- Borderline: Shows potential but has notable gaps
- No-Hire: Significant gaps that would require extensive training

Remember: This is a mock interview for learning. Be supportive while being truthful."""


async def generate_feedback(
    qa_history: List[Dict],
    seniority: str,
    role: str,
    strengths: List[str],
    gaps: List[str],
    final_scores: Dict[str, float]
) -> Dict[str, Any]:
    """
    Generate comprehensive feedback report.

    Returns:
        Dict with report, recommendation, and skill_roadmap
    """
    # Format Q&A history for the prompt
    qa_summary = []
    for i, qa in enumerate(qa_history, 1):
        qa_summary.append(f"""
Question {i}: {qa.get('question', 'N/A')}
Answer: {qa.get('answer', 'No answer provided')[:200]}...
Scores: Technical={qa.get('score', {}).get('technical', 'N/A')}, Design={qa.get('score', {}).get('design', 'N/A')}, Communication={qa.get('score', {}).get('communication', 'N/A')}
""")

    messages = [
        {"role": "system", "content": FEEDBACK_AGENT_PROMPT},
        {"role": "user", "content": f"""Generate a comprehensive feedback report.

INTERVIEW SUMMARY:
- Role: {role}
- Detected Seniority: {seniority}
- Number of Questions: {len(qa_history)}

FINAL AVERAGE SCORES:
- Technical: {final_scores.get('technical', 0)}/10
- Design: {final_scores.get('design', 0)}/10
- Communication: {final_scores.get('communication', 0)}/10

IDENTIFIED STRENGTHS: {', '.join(strengths)}
IDENTIFIED GAPS: {', '.join(gaps)}

Q&A HISTORY:
{''.join(qa_summary)}

Generate a feedback report with:
1. Overall assessment (2-3 sentences)
2. Detailed feedback for each scoring category
3. Hiring recommendation with clear justification
4. Learning roadmap with specific resources/topics

Return as JSON:
{{
    "report": "Full text report here (use markdown formatting)",
    "recommendation": "Hire/Borderline/No-Hire",
    "skill_roadmap": ["Specific learning recommendation 1", "...", "..."]
}}"""}
    ]

    response = chat_completion(messages, temperature=0.5, max_tokens=3000)
    content = response["content"]

    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())

        return {
            "report": data.get("report", "Thank you for completing this mock interview."),
            "recommendation": data.get("recommendation", "Borderline"),
            "skill_roadmap": data.get("skill_roadmap", ["Continue practicing technical concepts"])
        }
    except json.JSONDecodeError:
        # Generate basic report if JSON parsing fails
        avg_score = (
            final_scores.get('technical', 5) +
            final_scores.get('design', 5) +
            final_scores.get('communication', 5)
        ) / 3

        if avg_score >= 7:
            rec = "Hire"
        elif avg_score >= 5:
            rec = "Borderline"
        else:
            rec = "No-Hire"

        return {
            "report": f"""## Interview Feedback Report

### Overall Assessment
You completed a {len(qa_history)}-question interview for the {role} position.

### Scores
- Technical Understanding: {final_scores.get('technical', 5)}/10
- System Design: {final_scores.get('design', 5)}/10
- Communication: {final_scores.get('communication', 5)}/10

### Recommendation: {rec}

Thank you for participating in this mock interview. Continue practicing to improve your skills.""",
            "recommendation": rec,
            "skill_roadmap": gaps if gaps else ["Review core technical concepts"]
        }
