import enum
from datetime import datetime
from sqlalchemy import Integer, String, Text, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class SubmissionStatus(str, enum.Enum):
    PENDING = "Pending"
    JUDGING = "Judging"
    ACCEPTED = "Accepted"
    WRONG_ANSWER = "Wrong Answer"
    TIME_LIMIT_EXCEEDED = "TLE"
    RUNTIME_ERROR = "Runtime Error"
    SYSTEM_ERROR = "SYSTEM_ERROR"

class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_discord_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    problem_id: Mapped[int] = mapped_column(Integer, ForeignKey("problems.id"), nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    
    status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus), default=SubmissionStatus.PENDING)
    runtime: Mapped[float] = mapped_column(Float, nullable=True)
    memory: Mapped[float] = mapped_column(Float, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    problem = relationship("Problem", back_populates="submissions")