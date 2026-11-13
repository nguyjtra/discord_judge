from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.submission import SubmissionStatus

class SubmissionBase(BaseModel):
    user_discord_id: str
    problem_id: int
    source_code: str
    language: str

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionResponse(SubmissionBase):
    id: int
    status: SubmissionStatus
    runtime: Optional[float] = None
    memory: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
