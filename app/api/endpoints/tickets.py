from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketResponse

class TicketStatusUpdate(BaseModel):
    status: TicketStatus

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TicketResponse)
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = Ticket(**ticket_in.model_dump())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@router.get("/", response_model=list[TicketResponse])
def get_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.id.desc()).all()
    return tickets

@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket_status(ticket_id: int, body: TicketStatusUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Không tìm thấy ticket!")

    ticket.status = body.status
    if body.status == TicketStatus.RESOLVED:
        ticket.closed_at = datetime.utcnow()
    else:
        ticket.closed_at = None

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
