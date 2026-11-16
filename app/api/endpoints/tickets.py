from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.email_service import send_ticket_email

class TicketStatusUpdate(BaseModel):
    status: str

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def update_expired_tickets(db: Session):
    now = datetime.utcnow()
    open_tickets = db.query(Ticket).filter(
        Ticket.status.in_(["Open", "In-Progress"])
    ).all()

    has_changes = False
    for ticket in open_tickets:
        if ticket.deadline and now >= ticket.deadline:
            ticket.status = "Expired"
            has_changes = True

    if has_changes:
        db.commit()

@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket_in: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    priority_level = ticket_in.priority or "Necessary"

    if priority_level == "Priority":
        deadline_time = now + timedelta(minutes=15)
        duration_label = "15 minutes"
    else:
        priority_level = "Necessary"
        deadline_time = now + timedelta(hours=3)
        duration_label = "3 hours"

    new_ticket = Ticket(
        user_discord_id=ticket_in.user_discord_id,
        issue_description=ticket_in.issue_description,
        priority=priority_level,
        status="Open",
        created_at=now,
        deadline=deadline_time
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    background_tasks.add_task(
        send_ticket_email,
        new_ticket.id,
        new_ticket.user_discord_id,
        new_ticket.priority,
        new_ticket.issue_description,
        duration_label
    )

    return new_ticket

@router.get("/", response_model=list[TicketResponse])
def get_all_tickets(db: Session = Depends(get_db)):
    update_expired_tickets(db)
    tickets = db.query(Ticket).order_by(Ticket.id.desc()).all()
    return tickets

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, body: TicketStatusUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    ticket.status = body.status
    if body.status in ("Solved", "Resolved"):
        ticket.closed_at = datetime.utcnow()
    elif body.status == "Open":
        ticket.closed_at = None
        if ticket.priority == "Priority":
            ticket.deadline = datetime.utcnow() + timedelta(minutes=15)
        else:
            ticket.deadline = datetime.utcnow() + timedelta(hours=3)

    db.commit()
    db.refresh(ticket)
    return ticket

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted."}
