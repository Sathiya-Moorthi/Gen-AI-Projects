from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.session import InterviewSession, InterviewPhase
from app.schemas.session import SessionResponse

router = APIRouter()


@router.post("/start", response_model=SessionResponse)
async def start_session(db: Session = Depends(get_db)):
    """
    Create a new interview session.
    Returns a unique session ID for the interview.
    """
    try:
        session = InterviewSession(
            status="created",
            current_phase=InterviewPhase.SETUP,
            scores={"technical": 0, "design": 0, "communication": 0},
            qa_history=[],
            strengths=[],
            gaps=[],
            focus_areas=[],
            skill_roadmap=[]
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        return SessionResponse(
            session_id=session.id,
            status="created",
            message="Session created successfully. Upload resume and job description to continue."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}", response_model=dict)
async def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """
    Get session details by ID.
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == str(session_id)).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": str(session.id),
        "status": session.status,
        "current_phase": session.current_phase.value if session.current_phase else None,
        "detected_seniority": session.detected_seniority.value if session.detected_seniority else None,
        "has_resume": session.resume_text is not None,
        "has_jd": session.job_description is not None,
        "role": session.role,
        "memory_opt_in": session.memory_opt_in
    }
