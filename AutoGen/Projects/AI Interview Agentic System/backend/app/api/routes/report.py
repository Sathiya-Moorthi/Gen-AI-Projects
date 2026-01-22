from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.session import InterviewSession
from app.schemas.session import InterviewReport

router = APIRouter()


@router.get("/report/{session_id}", response_model=InterviewReport)
async def get_report(session_id: UUID, db: Session = Depends(get_db)):
    """
    Get the final interview report for a completed session.
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Calculate duration if interview has ended
    duration = None
    if session.started_at and session.ended_at:
        delta = session.ended_at - session.started_at
        duration = int(delta.total_seconds() / 60)

    return InterviewReport(
        session_id=session.id,
        status=session.status,
        detected_seniority=session.detected_seniority.value if session.detected_seniority else None,
        strengths=session.strengths or [],
        gaps=session.gaps or [],
        scores=session.scores or {"technical": 0, "design": 0, "communication": 0},
        qa_history=session.qa_history or [],
        final_report=session.final_report,
        recommendation=session.recommendation,
        skill_roadmap=session.skill_roadmap or [],
        duration_minutes=duration,
        started_at=session.started_at,
        ended_at=session.ended_at
    )
