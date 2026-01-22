import json
from typing import Dict, Any, List
from app.services.llm_service import chat_completion

QUESTION_GENERATOR_PROMPT = """You are an expert Technical Interview Question Generator Agent.

Your role is to generate thoughtful, role-appropriate interview questions. You must:

1. Generate ONLY theory and system design questions - NO coding questions
2. Match difficulty to the candidate's seniority level
3. Focus on the identified weak areas and focus topics
4. Ask one question at a time
5. Be transparent about difficulty level

Question types you can ask:
- Theoretical concepts (e.g., "Explain how garbage collection works")
- System design (e.g., "How would you design a rate limiter?")
- Architecture decisions (e.g., "When would you choose SQL vs NoSQL?")
- Real-world tradeoffs (e.g., "What are the tradeoffs of microservices?")
- Behavioral/situational technical scenarios

Difficulty mapping:
- Junior: Focus on fundamentals, basic concepts, simple scenarios
- Mid: Intermediate concepts, moderate system design, some tradeoffs
- Senior: Complex systems, architectural decisions, deep tradeoffs, leadership scenarios

Always explain WHY you're asking this question and what skill it tests.
Be encouraging and supportive - this is a learning-focused mock interview."""


async def generate_question(
    seniority: str,
    role: str,
    focus_areas: List[str],
    gaps: List[str],
    previous_questions: List[str],
    job_description: str
) -> Dict[str, Any]:
    """
    Generate the next interview question based on context.

    Returns:
        Dict with question, difficulty, topic, and explanation
    """
    messages = [
        {"role": "system", "content": QUESTION_GENERATOR_PROMPT},
        {"role": "user", "content": f"""Generate the next interview question.

CONTEXT:
- Role: {role}
- Seniority: {seniority}
- Focus Areas: {', '.join(focus_areas)}
- Skill Gaps to Explore: {', '.join(gaps)}
- Job Description Summary: {job_description[:500]}...

PREVIOUS QUESTIONS ASKED (avoid repetition):
{chr(10).join(['- ' + q for q in previous_questions]) if previous_questions else 'None yet - this is the first question'}

Generate a NEW question that:
1. Is appropriate for {seniority} level
2. Focuses on one of the gaps or focus areas
3. Is different from previous questions
4. Tests practical understanding, not memorization

Return as JSON:
{{
    "question": "Your interview question here",
    "difficulty": "easy/medium/hard",
    "topic": "The main topic this tests",
    "explanation": "Brief explanation of what this question assesses"
}}"""}
    ]

    response = chat_completion(messages, temperature=0.7)
    content = response["content"]

    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        question_data = json.loads(content.strip())

        return {
            "question": question_data.get("question", "Tell me about your experience with the technologies listed in your resume."),
            "difficulty": question_data.get("difficulty", "medium"),
            "topic": question_data.get("topic", "General"),
            "explanation": question_data.get("explanation", "This question assesses your overall understanding.")
        }
    except json.JSONDecodeError:
        return {
            "question": "Tell me about a challenging technical problem you've solved recently.",
            "difficulty": "medium",
            "topic": "Problem Solving",
            "explanation": "This assesses your problem-solving approach and technical depth."
        }
