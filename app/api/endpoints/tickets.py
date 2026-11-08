from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. API: User gửi báo cáo lỗi mới
@router.post("/", response_model=TicketResponse)
def create_ticket(ticket_in: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = Ticket(**ticket_in.model_dump())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

# 2. API: Lấy danh sách toàn bộ Ticket (dành cho Admin quản lý)
@router.get("/", response_model=list[TicketResponse])
def get_all_tickets(db: Session = Depends(get_db)):
    tickets = db.query(Ticket).all()
    return tickets