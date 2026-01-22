import json
from typing import Dict, Any, List
from app.services.llm_service import chat_completion

EVALUATION_AGENT_PROMPT = """You are an expert Technical Interview Evaluation Agent.

Your role is to score candidate answers objectively and provide constructive feedback.

SCORING CRITERIA (0-10 scale):
1. Technical Understanding (0-10):
   - Accuracy of technical concepts
   - Depth of knowledge demonstrated
   - Ability to explain complex topics

2. System Design Thinking (0-10):
   - Ability to break down problems
   - Consideration of tradeoffs
   - Scalability and maintainability awareness

3. Communication Clarity (0-10):
   - Structure and organization of response
   - Ability to articulate thoughts clearly
   - Use of examples to illustrate points

IMPORTANT RULES:
- Do NOT penalize grammar mistakes or accent
- Do NOT penalize nervousness or hesitation
- DO value reasoning over memorization
- DO give credit for honest "I don't know" + good reasoning
- Adjust expectations based on seniority level

Be encouraging and constructive. This is a learning-focused interview.
Provide specific, actionable feedback."""


async def evaluate_answer(
    question: str,
    answer: str,
    seniority: str,
    topic: str
) -> Dict[str, Any]:
    """
    Evaluate a candidate's answer and provide scores and feedback.

    Returns:
        Dict with scores (technical, design, communication) and feedback
    """
    messages = [
        {"role": "system", "content": EVALUATION_AGENT_PROMPT},
        {"role": "user", "content": f"""Evaluate this interview response.

QUESTION:
{question}

CANDIDATE'S ANSWER:
{answer}

CONTEXT:
- Topic: {topic}
- Candidate Seniority: {seniority}

Provide scores and feedback. Be fair to their experience level.
A junior giving a solid fundamental answer should score well for junior level.

Return as JSON:
{{
    "scores": {{
        "technical": 0-10,
        "design": 0-10,
        "communication": 0-10
    }},
    "feedback": "Constructive feedback on the answer",
    "strengths": ["What they did well"],
    "improvements": ["What could be improved"]
}}"""}
    ]

    response = chat_completion(messages, temperature=0.4)
    content = response["content"]

    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())

        scores = data.get("scores", {})
        return {
            "scores": {
                "technical": min(10, max(0, scores.get("technical", 5))),
                "design": min(10, max(0, scores.get("design", 5))),
                "communication": min(10, max(0, scores.get("communication", 5)))
            },
            "feedback": data.get("feedback", "Good effort on this question."),
            "strengths": data.get("strengths", []),
            "improvements": data.get("improvements", [])
        }
    except json.JSONDecodeError:
        return {
            "scores": {"technical": 5, "design": 5, "communication": 5},
            "feedback": "Thank you for your response.",
            "strengths": [],
            "improvements": []
        }


def calculate_running_average(qa_history: List[Dict]) -> Dict[str, float]:
    """Calculate running average scores from Q&A history."""
    if not qa_history:
        return {"technical": 0, "design": 0, "communication": 0}

    totals = {"technical": 0, "design": 0, "communication": 0}
    count = 0

    for qa in qa_history:
        if "score" in qa and qa["score"]:
            scores = qa["score"]
            totals["technical"] += scores.get("technical", 0)
            totals["design"] += scores.get("design", 0)
            totals["communication"] += scores.get("communication", 0)
            count += 1

    if count == 0:
        return {"technical": 0, "design": 0, "communication": 0}

    return {
        "technical": round(totals["technical"] / count, 1),
        "design": round(totals["design"] / count, 1),
        "communication": round(totals["communication"] / count, 1)
    }
