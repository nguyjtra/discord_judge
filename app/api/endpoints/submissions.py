from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API: Nhận code từ Discord gửi về
@router.post("/", response_model=SubmissionResponse)
def submit_code(submission_in: SubmissionCreate, db: Session = Depends(get_db)):
    new_submission = Submission(**submission_in.model_dump())
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    # LƯU Ý CHO TƯƠNG LAI: 
    # Sau này chúng ta sẽ viết thêm code ở đây để gọi Docker Sandbox chấm bài
    
    return new_submission