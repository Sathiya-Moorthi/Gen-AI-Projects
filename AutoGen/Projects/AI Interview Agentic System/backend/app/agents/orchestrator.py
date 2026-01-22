import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from app.models.session import InterviewPhase


class OrchestratorAgent:
    """
    Orchestrator Agent controls the interview flow.

    Responsibilities:
    - Track interview time (30-45 min)
    - Maintain interview state/phase
    - Coordinate other agents
    - Ensure transparency with the candidate
    - Handle graceful transitions
    """

    def __init__(
        self,
        session_id: str,
        duration_minutes: int = 35,
        on_phase_change: Optional[Callable] = None,
        on_time_update: Optional[Callable] = None
    ):
        self.session_id = session_id
        self.duration_minutes = duration_minutes
        self.current_phase = InterviewPhase.SETUP
        self.started_at: Optional[datetime] = None
        self.question_count = 0
        self.max_questions = 8
        self.followup_count = 0
        self.current_question_followups = 0

        # Callbacks for WebSocket updates
        self.on_phase_change = on_phase_change
        self.on_time_update = on_time_update

    def start_interview(self) -> Dict[str, Any]:
        """Start the interview timer and transition to analyzing phase."""
        self.started_at = datetime.utcnow()
        self.current_phase = InterviewPhase.ANALYZING
        return {
            "phase": self.current_phase.value,
            "message": "Interview started. Analyzing your profile...",
            "time_remaining": self.duration_minutes * 60
        }

    def get_time_remaining(self) -> int:
        """Get remaining time in seconds."""
        if not self.started_at:
            return self.duration_minutes * 60

        elapsed = datetime.utcnow() - self.started_at
        remaining = (self.duration_minutes * 60) - elapsed.total_seconds()
        return max(0, int(remaining))

    def is_time_up(self) -> bool:
        """Check if interview time has expired."""
        return self.get_time_remaining() <= 0

    def should_end_interview(self) -> bool:
        """Determine if interview should end."""
        return (
            self.is_time_up() or
            self.question_count >= self.max_questions or
            self.current_phase == InterviewPhase.COMPLETED
        )

    def transition_phase(self, new_phase: InterviewPhase) -> Dict[str, Any]:
        """Transition to a new interview phase."""
        old_phase = self.current_phase
        self.current_phase = new_phase

        messages = {
            InterviewPhase.ANALYZING: "Analyzing your resume and the job requirements...",
            InterviewPhase.INTRO: "Let me introduce myself and explain how this interview will work.",
            InterviewPhase.QUESTIONS: "Now I'll ask you some technical questions.",
            InterviewPhase.FOLLOWUP: "I'd like to explore that answer a bit more.",
            InterviewPhase.EVALUATION: "Evaluating your responses...",
            InterviewPhase.FEEDBACK: "Generating your personalized feedback report...",
            InterviewPhase.COMPLETED: "Interview completed! Here's your feedback."
        }

        result = {
            "previous_phase": old_phase.value,
            "current_phase": new_phase.value,
            "message": messages.get(new_phase, "Transitioning..."),
            "time_remaining": self.get_time_remaining()
        }

        if self.on_phase_change:
            asyncio.create_task(self.on_phase_change(result))

        return result

    def record_question(self):
        """Record that a question was asked."""
        self.question_count += 1
        self.current_question_followups = 0

    def record_followup(self):
        """Record a follow-up question."""
        self.followup_count += 1
        self.current_question_followups += 1

    def can_ask_followup(self) -> bool:
        """Check if more follow-ups are allowed for current question."""
        return self.current_question_followups < 2

    def get_interview_intro(self, seniority: str, role: str, focus_areas: list) -> str:
        """Generate personalized interview introduction."""
        return f"""Welcome to your mock interview for the **{role}** position!

Based on your resume, I've identified you as a **{seniority.capitalize()}-level** candidate.

**How this interview works:**
- I'll ask you {self.max_questions-2} to {self.max_questions} technical questions
- Questions will focus on theory and system design (no coding)
- We have about {self.duration_minutes} minutes
- I might ask follow-up questions to understand your thinking
- Your scores will be visible throughout (full transparency!)

**Today's focus areas:**
{chr(10).join(['- ' + area for area in focus_areas])}

Feel free to ask me to clarify any question. This is a learning experience, so don't stress!

Ready to begin?"""

    def get_status(self) -> Dict[str, Any]:
        """Get current interview status."""
        return {
            "session_id": self.session_id,
            "phase": self.current_phase.value,
            "questions_asked": self.question_count,
            "max_questions": self.max_questions,
            "time_remaining": self.get_time_remaining(),
            "is_time_up": self.is_time_up(),
            "should_end": self.should_end_interview()
        }
