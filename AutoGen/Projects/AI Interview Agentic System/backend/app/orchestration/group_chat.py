"""
AutoGen GroupChat configuration for the interview system.

This module sets up the AutoGen agents and their interaction patterns.
Agents are coordinated to run sequentially based on interview phase.
"""

from typing import Dict, Any, List, Optional
import autogen
from app.core.config import settings


def get_llm_config() -> Dict[str, Any]:
    """Get LLM configuration for AutoGen agents."""
    return {
        "config_list": [
            {
                "model": "gpt-4o",
                "api_key": settings.OPENAI_API_KEY,
            }
        ],
        "temperature": 0.7,
    }


def create_autogen_agents() -> Dict[str, autogen.AssistantAgent]:
    """
    Create AutoGen agents for the interview system.

    Returns dict of agent name -> agent instance.
    """
    llm_config = get_llm_config()

    # Orchestrator - coordinates the interview flow
    orchestrator = autogen.AssistantAgent(
        name="Orchestrator",
        system_message="""You are the Interview Orchestrator. You control the flow of the interview:
- Manage timing (30-45 minutes total)
- Transition between phases smoothly
- Be transparent about the process
- Keep the interview on track
- Signal when to move to the next question or phase""",
        llm_config=llm_config,
    )

    # Resume Analyzer
    resume_analyzer = autogen.AssistantAgent(
        name="ResumeAnalyzer",
        system_message="""You analyze candidate resumes to determine:
- Seniority level (junior/mid/senior)
- Key strengths
- Skill gaps
- Focus areas for the interview
Be thorough but concise.""",
        llm_config=llm_config,
    )

    # Question Generator
    question_generator = autogen.AssistantAgent(
        name="QuestionGenerator",
        system_message="""You generate technical interview questions:
- Theory and system design only (NO coding)
- Match difficulty to seniority
- Focus on identified gaps
- One question at a time
- Explain what each question tests""",
        llm_config=llm_config,
    )

    # Follow-up Agent
    followup_agent = autogen.AssistantAgent(
        name="FollowupAgent",
        system_message="""You determine if follow-up questions are needed:
- Probe vague answers
- Explore partial understanding
- Clarify reasoning
- Never assume - ask instead
Maximum 2 follow-ups per question.""",
        llm_config=llm_config,
    )

    # Evaluation Agent
    evaluator = autogen.AssistantAgent(
        name="Evaluator",
        system_message="""You evaluate candidate answers:
- Score 0-10: Technical, Design, Communication
- Don't penalize grammar or nervousness
- Value reasoning over memorization
- Provide constructive feedback""",
        llm_config=llm_config,
    )

    # Feedback Agent
    feedback_agent = autogen.AssistantAgent(
        name="FeedbackAgent",
        system_message="""You generate final interview feedback:
- Comprehensive report
- Hire/Borderline/No-Hire recommendation
- Skill roadmap for improvement
- Be honest but encouraging""",
        llm_config=llm_config,
    )

    return {
        "orchestrator": orchestrator,
        "resume_analyzer": resume_analyzer,
        "question_generator": question_generator,
        "followup_agent": followup_agent,
        "evaluator": evaluator,
        "feedback_agent": feedback_agent,
    }


def create_group_chat(agents: Dict[str, autogen.AssistantAgent]) -> autogen.GroupChat:
    """
    Create AutoGen GroupChat with all interview agents.

    The group chat coordinates agent interactions.
    """
    agent_list = list(agents.values())

    groupchat = autogen.GroupChat(
        agents=agent_list,
        messages=[],
        max_round=100,
        speaker_selection_method="auto",  # LLM decides next speaker
    )

    return groupchat


def create_manager(groupchat: autogen.GroupChat) -> autogen.GroupChatManager:
    """Create GroupChat manager to coordinate agents."""
    llm_config = get_llm_config()

    manager = autogen.GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config,
    )

    return manager
