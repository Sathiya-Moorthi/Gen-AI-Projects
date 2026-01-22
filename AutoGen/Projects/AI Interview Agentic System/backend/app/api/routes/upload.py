from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.session import InterviewSession, Seniority
from app.schemas.session import ResumeUpload, JDUploadResponse
from app.services.document_parser import parse_document
from app.agents.resume_analyzer import analyze_resume

router = APIRouter()


@router.post("/resume", response_model=ResumeUpload)
async def upload_resume(
    session_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse resume (PDF, DOCX, or TXT).
    Analyzes resume to detect seniority, strengths, and gaps.
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # Parse the document
        content = await file.read()
        resume_text = parse_document(content, file.filename)

        # Store raw resume text
        session.resume_text = resume_text

        # Analyze resume if JD is already uploaded
        if session.job_description:
            analysis = await analyze_resume(
                resume_text=resume_text,
                job_description=session.job_description,
                role=session.role or "Software Engineer"
            )
            session.detected_seniority = Seniority(analysis["seniority"])
            session.strengths = analysis["strengths"]
            session.gaps = analysis["gaps"]
            session.focus_areas = analysis["focus_areas"]

        db.commit()
        db.refresh(session)

        return ResumeUpload(
            session_id=session.id,
            resume_received=True,
            detected_seniority=session.detected_seniority.value if session.detected_seniority else None,
            strengths=session.strengths or [],
            gaps=session.gaps or [],
            focus_areas=session.focus_areas or []
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@router.post("/jd", response_model=JDUploadResponse)
async def upload_jd(
    session_id: UUID = Form(...),
    job_description: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload job description and role.
    If resume is already uploaded, triggers analysis.
    """
    session = db.query(InterviewSession).filter(InterviewSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        session.job_description = job_description
        session.role = role

        # Analyze if resume is already uploaded
        if session.resume_text:
            analysis = await analyze_resume(
                resume_text=session.resume_text,
                job_description=job_description,
                role=role
            )
            session.detected_seniority = Seniority(analysis["seniority"])
            session.strengths = analysis["strengths"]
            session.gaps = analysis["gaps"]
            session.focus_areas = analysis["focus_areas"]

        db.commit()
        db.refresh(session)

        return JDUploadResponse(
            session_id=session.id,
            jd_received=True,
            role=role
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process JD: {str(e)}")
