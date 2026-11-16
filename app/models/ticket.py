import enum
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class TicketPriority(str, enum.Enum):
    PRIORITY = "Priority"
    NECESSARY = "Necessary"

class TicketStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In-Progress"
    SOLVED = "Solved"
    RESOLVED = "Resolved"
    EXPIRED = "Expired"

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_discord_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default=TicketPriority.NECESSARY.value)
    status: Mapped[str] = mapped_column(String(50), default=TicketStatus.OPEN.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
