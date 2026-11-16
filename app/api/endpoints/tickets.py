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

def cap_nhat_ticket_het_han(db: Session):
    now = datetime.utcnow()
    cac_ticket_dang_mo = db.query(Ticket).filter(
        Ticket.status.in_(["Open", "In-Progress"])
    ).all()

    co_thay_doi = False
    for t in cac_ticket_dang_mo:
        if t.deadline and now >= t.deadline:
            t.status = "Expired"
            co_thay_doi = True

    if co_thay_doi:
        db.commit()

@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket_in: TicketCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    loai_uu_tien = ticket_in.priority or "Necessary"

    if loai_uu_tien == "Priority":
        han_xu_ly = now + timedelta(minutes=15)
        thoi_gian_chu = "15 minutes"
    else:
        loai_uu_tien = "Necessary"
        han_xu_ly = now + timedelta(hours=3)
        thoi_gian_chu = "3 hours"

    new_ticket = Ticket(
        user_discord_id=ticket_in.user_discord_id,
        issue_description=ticket_in.issue_description,
        priority=loai_uu_tien,
        status="Open",
        created_at=now,
        deadline=han_xu_ly
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
        thoi_gian_chu
    )

    return new_ticket

@router.get("/", response_model=list[TicketResponse])
def get_all_tickets(db: Session = Depends(get_db)):
    cap_nhat_ticket_het_han(db)
    tickets = db.query(Ticket).order_by(Ticket.id.desc()).all()
    return tickets

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, body: TicketStatusUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy ticket!")

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
        raise HTTPException(status_code=404, detail="Không tìm thấy ticket!")
    db.delete(ticket)
    db.commit()
    return {"message": "Đã xóa ticket!"}
