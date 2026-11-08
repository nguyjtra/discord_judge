from sqlalchemy.orm import Session
from app.models.submission import Submission, SubmissionStatus
from app.workers.sandbox_worker import run_python_code

def process_submission(db: Session, submission_id: int):
    """
    Hàm này sẽ được gọi chạy ngầm: 
    Lấy code từ DB -> Nhét vào Sandbox -> Cập nhật trạng thái
    """
    # 1. Tìm bài nộp trong Database
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        return

    # 2. Gọi Hộp cát chạy code
    result = run_python_code(submission.source_code)

    # 3. Cập nhật thời gian chạy
    submission.runtime = result["runtime"]

    # 4. Phân tích kết quả và cập nhật trạng thái
    if result["status"] == "Success":
        submission.status = SubmissionStatus.ACCEPTED
    else:
        submission.status = SubmissionStatus.RUNTIME_ERROR

    # 5. Lưu kết quả mới vào MySQL
    db.commit()