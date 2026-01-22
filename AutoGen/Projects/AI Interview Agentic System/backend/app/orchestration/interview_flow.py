"""
Interview Flow State Machine

Manages the state and transitions of an interview session.
Coordinates the various agents through the interview phases.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.session import InterviewSession, InterviewPhase, Seniority
from app.agents.orchestrator import OrchestratorAgent
from app.agents.question_generator import generate_question
from app.agents.followup import check_followup
from app.agents.evaluation import evaluate_answer, calculate_running_average
from app.agents.feedback import generate_feedback
from app.agents.memory_agent import MemoryAgent


class InterviewFlow:
    """
    Manages the complete interview flow from start to finish.

    State Machine:
    SETUP → ANALYZING → INTRO → QUESTIONS ↔ FOLLOWUP → EVALUATION → FEEDBACK → COMPLETED
    """

    def __init__(
        self,
        session: InterviewSession,
        db: Session,
        send_message: Callable
    ):
        self.session = session
        self.db = db
        self.send_message = send_message  # Callback to send WebSocket messages

        self.orchestrator = OrchestratorAgent(
            session_id=str(session.id),
            duration_minutes=int(session.duration_minutes or 35)
        )

        self.memory_agent = MemoryAgent(str(session.id), db)

        # Current question state
        self.current_question: Optional[Dict] = None
        self.current_followup_count = 0
        self.previous_questions: List[str] = []

    async def start(self) -> Dict[str, Any]:
        """Start the interview."""
        # Update session
        self.session.started_at = datetime.utcnow()
        self.session.status = "active"
        self.db.commit()

        # Start orchestrator
        start_info = self.orchestrator.start_interview()

        # Transition to intro phase
        await self._transition_to_intro()

        return start_info

    async def _transition_to_intro(self):
        """Transition to intro phase and send introduction."""
        self.orchestrator.transition_phase(InterviewPhase.INTRO)
        self.session.current_phase = InterviewPhase.INTRO
        self.db.commit()

        intro = self.orchestrator.get_interview_intro(
            seniority=self.session.detected_seniority.value if self.session.detected_seniority else "mid",
            role=self.session.role or "Software Engineer",
            focus_areas=self.session.focus_areas or []
        )

        await self.send_message({
            "type": "intro",
            "data": {
                "message": intro,
                "phase": "intro",
                "seniority": self.session.detected_seniority.value if self.session.detected_seniority else "mid",
                "focus_areas": self.session.focus_areas or []
            }
        })

    async def generate_next_question(self) -> Dict[str, Any]:
        """Generate and send the next interview question."""
        # Check if we should end
        if self.orchestrator.should_end_interview():
            return await self.end_interview()

        # Transition to questions phase
        self.orchestrator.transition_phase(InterviewPhase.QUESTIONS)
        self.session.current_phase = InterviewPhase.QUESTIONS
        self.db.commit()

        # Generate question
        question_data = await generate_question(
            seniority=self.session.detected_seniority.value if self.session.detected_seniority else "mid",
            role=self.session.role or "Software Engineer",
            focus_areas=self.session.focus_areas or [],
            gaps=self.session.gaps or [],
            previous_questions=self.previous_questions,
            job_description=self.session.job_description or ""
        )

        self.current_question = question_data
        self.current_followup_count = 0
        self.previous_questions.append(question_data["question"])
        self.orchestrator.record_question()

        await self.send_message({
            "type": "new_question",
            "data": {
                "question": question_data["question"],
                "difficulty": question_data["difficulty"],
                "topic": question_data["topic"],
                "explanation": question_data["explanation"],
                "question_number": self.orchestrator.question_count,
                "time_remaining": self.orchestrator.get_time_remaining()
            }
        })

        return question_data

    async def process_answer(self, answer: str) -> Dict[str, Any]:
        """Process candidate's answer."""
        if not self.current_question:
            return {"error": "No active question"}

        # Evaluate the answer
        evaluation = await evaluate_answer(
            question=self.current_question["question"],
            answer=answer,
            seniority=self.session.detected_seniority.value if self.session.detected_seniority else "mid",
            topic=self.current_question.get("topic", "General")
        )

        # Store Q&A
        qa_item = {
            "question": self.current_question["question"],
            "answer": answer,
            "score": evaluation["scores"],
            "feedback": evaluation["feedback"],
            "topic": self.current_question.get("topic", "General")
        }

        # Update session Q&A history
        qa_history = self.session.qa_history or []
        qa_history.append(qa_item)
        self.session.qa_history = qa_history

        # Calculate running averages
        running_scores = calculate_running_average(qa_history)
        self.session.scores = running_scores
        self.db.commit()

        # Send score update
        await self.send_message({
            "type": "score_update",
            "data": {
                "current_scores": evaluation["scores"],
                "running_average": running_scores,
                "feedback": evaluation["feedback"],
                "strengths": evaluation.get("strengths", []),
                "improvements": evaluation.get("improvements", [])
            }
        })

        # Check if follow-up is needed
        followup_data = await check_followup(
            original_question=self.current_question["question"],
            candidate_answer=answer,
            seniority=self.session.detected_seniority.value if self.session.detected_seniority else "mid",
            followup_count=self.current_followup_count
        )

        if followup_data["needs_followup"] and self.orchestrator.can_ask_followup():
            return await self._ask_followup(followup_data)
        else:
            # Move to next question or end
            if self.orchestrator.should_end_interview():
                return await self.end_interview()
            else:
                return await self.generate_next_question()

    async def _ask_followup(self, followup_data: Dict) -> Dict[str, Any]:
        """Ask a follow-up question."""
        self.orchestrator.transition_phase(InterviewPhase.FOLLOWUP)
        self.orchestrator.record_followup()
        self.current_followup_count += 1

        self.session.current_phase = InterviewPhase.FOLLOWUP
        self.db.commit()

        # Update current question to the follow-up
        self.current_question = {
            "question": followup_data["followup_question"],
            "difficulty": self.current_question.get("difficulty", "medium"),
            "topic": self.current_question.get("topic", "General"),
            "is_followup": True
        }

        await self.send_message({
            "type": "followup",
            "data": {
                "question": followup_data["followup_question"],
                "reason": followup_data["reason"],
                "time_remaining": self.orchestrator.get_time_remaining()
            }
        })

        return followup_data

    async def end_interview(self) -> Dict[str, Any]:
        """End the interview and generate feedback."""
        # Transition to evaluation
        self.orchestrator.transition_phase(InterviewPhase.EVALUATION)
        self.session.current_phase = InterviewPhase.EVALUATION
        self.db.commit()

        await self.send_message({
            "type": "phase_update",
            "data": {
                "phase": "evaluation",
                "message": "Evaluating your overall performance..."
            }
        })

        # Calculate final scores
        final_scores = calculate_running_average(self.session.qa_history or [])

        # Transition to feedback
        self.orchestrator.transition_phase(InterviewPhase.FEEDBACK)
        self.session.current_phase = InterviewPhase.FEEDBACK
        self.db.commit()

        await self.send_message({
            "type": "phase_update",
            "data": {
                "phase": "feedback",
                "message": "Generating your personalized feedback report..."
            }
        })

        # Generate feedback
        feedback = await generate_feedback(
            qa_history=self.session.qa_history or [],
            seniority=self.session.detected_seniority.value if self.session.detected_seniority else "mid",
            role=self.session.role or "Software Engineer",
            strengths=self.session.strengths or [],
            gaps=self.session.gaps or [],
            final_scores=final_scores
        )

        # Update session
        self.session.final_report = feedback["report"]
        self.session.recommendation = feedback["recommendation"]
        self.session.skill_roadmap = feedback["skill_roadmap"]
        self.session.ended_at = datetime.utcnow()
        self.session.status = "completed"
        self.session.current_phase = InterviewPhase.COMPLETED
        self.db.commit()

        # Store to memory if opted in
        if self.session.memory_opt_in:
            await self.memory_agent.finalize_session(
                final_report=feedback["report"],
                recommendation=feedback["recommendation"],
                skill_roadmap=feedback["skill_roadmap"]
            )

        await self.send_message({
            "type": "feedback",
            "data": {
                "report": feedback["report"],
                "recommendation": feedback["recommendation"],
                "skill_roadmap": feedback["skill_roadmap"],
                "final_scores": final_scores,
                "phase": "completed"
            }
        })

        return feedback

    def get_status(self) -> Dict[str, Any]:
        """Get current interview status."""
        return {
            **self.orchestrator.get_status(),
            "qa_count": len(self.session.qa_history or []),
            "current_scores": self.session.scores
        }
