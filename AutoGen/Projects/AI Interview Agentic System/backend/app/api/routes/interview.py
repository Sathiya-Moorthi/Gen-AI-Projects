from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.session import InterviewSession
from app.schemas.session import MemoryOptIn, MemoryOptInResponse

router = APIRouter()


@router.post("/opt-in-memory", response_model=MemoryOptInResponse)
async def opt_in_memory(
    session_id: UUID,
    opt_in: MemoryOptIn,
    db: Session = Depends(get_db)
):
    """
    Toggle memory storage opt-in for the session.
    When opted in, interview data will be stored for future reference.
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        session.memory_opt_in = opt_in.opt_in
        db.commit()
        db.refresh(session)

        message = (
            "Memory storage enabled. Your interview data will be saved for future sessions."
            if opt_in.opt_in
            else "Memory storage disabled. Your interview data will not be saved."
        )

        return MemoryOptInResponse(
            session_id=session.id,
            memory_opt_in=session.memory_opt_in,
            message=message
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update memory preference: {str(e)}")
