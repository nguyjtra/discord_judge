from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.ticket import TicketStatus

class TicketBase(BaseModel):
    user_discord_id: str
    issue_description: str

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: int
    status: TicketStatus
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
