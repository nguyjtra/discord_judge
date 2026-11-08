import enum
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class TicketStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In-Progress"
    RESOLVED = "Resolved"

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_discord_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)