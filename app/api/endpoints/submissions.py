from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.judge_service import process_submission

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=SubmissionResponse)
def submit_code(
    submission_in: SubmissionCreate, 
    background_tasks: BackgroundTasks,  # Thêm công cụ chạy ngầm
    db: Session = Depends(get_db)
):
    # 1. Lưu bài nộp vào Database với trạng thái mặc định là Pending
    new_submission = Submission(**submission_in.model_dump())
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    # 2. Bắn tín hiệu cho hàm chấm bài chạy ngầm ở chế độ nền
    # User sẽ nhận được phản hồi ngay lập tức mà không phải chờ Docker chạy xong
    background_tasks.add_task(process_submission, new_submission.id)
    
    return new_submission