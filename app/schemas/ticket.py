from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketBase(BaseModel):
    user_discord_id: str
    issue_description: str
    priority: Optional[str] = "Necessary"

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: int
    status: str
    created_at: datetime
    deadline: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
