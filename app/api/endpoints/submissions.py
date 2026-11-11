from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.judge_service import process_submission
from app.models.submission import SubmissionStatus
from app.services.ai_service import explain_code_error
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
    # nén bài tập chạy song song 
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

@router.get("/", response_model=list[SubmissionResponse])
def get_all_submissions(db: Session = Depends(get_db)):
    return db.query(Submission).order_by(Submission.id.desc()).limit(50).all()

@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="ID not found.")
    return submission

# API MỚI: Yêu cầu AI giải thích lỗi của một bài nộp cụ thể
@router.get("/{submission_id}/explain")
def explain_submission_error(submission_id: int, db: Session = Depends(get_db)):
    # 1. Tìm bài nộp trong Database
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        return {"message": "Error"}
    explanation = explain_code_error(submission.source_code)
    return {
        "submission_id": submission.id,
        "ai_explanation": explanation
    }
