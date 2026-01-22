import json
from typing import Dict, Any, Optional
from app.services.llm_service import chat_completion

FOLLOWUP_AGENT_PROMPT = """You are an expert Follow-up Interview Agent.

Your role is to determine if a candidate's answer needs clarification and generate appropriate follow-up questions.

You should ask follow-up questions when:
1. The answer is vague or lacks specific details
2. The candidate shows partial understanding but missed key points
3. The reasoning is unclear or incomplete
4. There's an interesting point worth exploring deeper
5. Technical accuracy needs verification

You should NOT ask follow-up when:
1. The answer is complete and demonstrates full understanding
2. The candidate clearly doesn't know (move on instead)
3. You've already asked 2+ follow-ups on the same question

Be supportive and encouraging. Frame follow-ups as curiosity, not criticism.
Help the candidate showcase their knowledge.

Output JSON with:
- needs_followup: boolean
- followup_question: string (if needed)
- reason: why you're asking (shared with candidate for transparency)"""


async def check_followup(
    original_question: str,
    candidate_answer: str,
    seniority: str,
    followup_count: int = 0
) -> Dict[str, Any]:
    """
    Determine if follow-up is needed and generate it.

    Returns:
        Dict with needs_followup, followup_question (if any), and reason
    """
    if followup_count >= 2:
        return {
            "needs_followup": False,
            "followup_question": None,
            "reason": "Maximum follow-ups reached for this question"
        }

    messages = [
        {"role": "system", "content": FOLLOWUP_AGENT_PROMPT},
        {"role": "user", "content": f"""Analyze this Q&A and determine if follow-up is needed.

ORIGINAL QUESTION:
{original_question}

CANDIDATE'S ANSWER:
{candidate_answer}

CANDIDATE SENIORITY: {seniority}
FOLLOW-UPS ALREADY ASKED: {followup_count}

Consider:
1. Is the answer complete for their seniority level?
2. Are there gaps in understanding?
3. Is there something worth exploring deeper?

Return as JSON:
{{
    "needs_followup": true/false,
    "followup_question": "Your follow-up question if needed",
    "reason": "Why you're asking this (will be shown to candidate)"
}}"""}
    ]

    response = chat_completion(messages, temperature=0.5)
    content = response["content"]

    try:
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        data = json.loads(content.strip())

        return {
            "needs_followup": data.get("needs_followup", False),
            "followup_question": data.get("followup_question"),
            "reason": data.get("reason", "Exploring your understanding further")
        }
    except json.JSONDecodeError:
        return {
            "needs_followup": False,
            "followup_question": None,
            "reason": "Proceeding to next question"
        }
