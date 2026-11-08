from app.models.submission import Submission, SubmissionStatus
from app.workers.sandbox_worker import run_python_code
from app.db.session import SessionLocal

def process_submission(submission_id: int):
    # Tự tạo một kết nối Database ĐỘC LẬP cho tiến trình chạy ngầm
    db = SessionLocal()
    try:
        # 1. Tìm bài nộp trong Database
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            return

        # 2. Gọi Hộp cát chạy code
        result = run_python_code(submission.source_code)

        # 3. Cập nhật kết quả
        submission.runtime = result["runtime"]

        if result["status"] == "Success":
            submission.status = SubmissionStatus.ACCEPTED
        else:
            submission.status = SubmissionStatus.RUNTIME_ERROR

        # 4. Lưu vào MySQL
        db.commit()
    except Exception as e:
        print("Lỗi khi chấm bài:", e)
    finally:
        # 5. Xong việc thì đóng cửa kết nối
        db.close()