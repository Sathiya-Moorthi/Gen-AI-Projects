from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class SessionCreate(BaseModel):
    """Request model for creating a new session."""
    pass  # No input required for session creation


class SessionResponse(BaseModel):
    """Response model for session operations."""
    session_id: UUID
    status: str
    message: str

    class Config:
        from_attributes = True


class ResumeUpload(BaseModel):
    """Response model after resume upload."""
    session_id: UUID
    resume_received: bool
    detected_seniority: Optional[str] = None
    strengths: List[str] = []
    gaps: List[str] = []
    focus_areas: List[str] = []


class JDUpload(BaseModel):
    """Request model for JD upload."""
    job_description: str
    role: str


class JDUploadResponse(BaseModel):
    """Response model after JD upload."""
    session_id: UUID
    jd_received: bool
    role: str


class MemoryOptIn(BaseModel):
    """Request model for memory opt-in."""
    opt_in: bool


class MemoryOptInResponse(BaseModel):
    """Response model for memory opt-in."""
    session_id: UUID
    memory_opt_in: bool
    message: str


class ScoreUpdate(BaseModel):
    """Model for score updates."""
    technical: int = 0
    design: int = 0
    communication: int = 0


class QAItem(BaseModel):
    """Model for question-answer pairs."""
    question: str
    difficulty: str
    answer: Optional[str] = None
    score: Optional[Dict[str, int]] = None
    feedback: Optional[str] = None


class InterviewReport(BaseModel):
    """Response model for the final interview report."""
    session_id: UUID
    status: str
    detected_seniority: Optional[str]
    strengths: List[str]
    gaps: List[str]
    scores: Dict[str, int]
    qa_history: List[Dict[str, Any]]
    final_report: Optional[str]
    recommendation: Optional[str]
    skill_roadmap: List[str]
    duration_minutes: Optional[int]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
