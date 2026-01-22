"""
PostgreSQL Session Store

Handles persistence of interview session data including:
- Session metadata
- Q&A history
- Scores
- Final reports
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.session import InterviewSession, InterviewPhase


class SessionStore:
    """
    PostgreSQL-based storage for interview sessions.

    Handles all session-related database operations.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """Get session by ID."""
        try:
            uuid = UUID(session_id)
            return self.db.query(InterviewSession).filter(
                InterviewSession.id == uuid
            ).first()
        except ValueError:
            return None

    def add_qa_to_session(self, session_id: str, qa_item: Dict[str, Any]):
        """Add a Q&A item to session history."""
        session = self.get_session(session_id)
        if not session:
            return

        qa_history = session.qa_history or []
        qa_history.append(qa_item)
        session.qa_history = qa_history
        self.db.commit()

    def update_scores(self, session_id: str, scores: Dict[str, float]):
        """Update running average scores."""
        session = self.get_session(session_id)
        if not session:
            return

        session.scores = scores
        self.db.commit()

    def update_phase(self, session_id: str, phase: InterviewPhase):
        """Update current interview phase."""
        session = self.get_session(session_id)
        if not session:
            return

        session.current_phase = phase
        self.db.commit()

    def finalize_session(
        self,
        session_id: str,
        final_report: str,
        recommendation: str,
        skill_roadmap: List[str]
    ):
        """Finalize session with report and recommendation."""
        session = self.get_session(session_id)
        if not session:
            return

        session.final_report = final_report
        session.recommendation = recommendation
        session.skill_roadmap = skill_roadmap
        session.status = "completed"
        session.current_phase = InterviewPhase.COMPLETED
        session.ended_at = datetime.utcnow()
        self.db.commit()

    def get_past_sessions(
        self,
        limit: int = 10,
        completed_only: bool = True
    ) -> List[InterviewSession]:
        """Get past interview sessions."""
        query = self.db.query(InterviewSession)

        if completed_only:
            query = query.filter(InterviewSession.status == "completed")

        return query.order_by(
            InterviewSession.created_at.desc()
        ).limit(limit).all()

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": str(session.id),
            "role": session.role,
            "seniority": session.detected_seniority.value if session.detected_seniority else None,
            "status": session.status,
            "scores": session.scores,
            "recommendation": session.recommendation,
            "questions_count": len(session.qa_history or []),
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "duration_minutes": self._calculate_duration(session)
        }

    def _calculate_duration(self, session: InterviewSession) -> Optional[int]:
        """Calculate session duration in minutes."""
        if session.started_at and session.ended_at:
            delta = session.ended_at - session.started_at
            return int(delta.total_seconds() / 60)
        return None
