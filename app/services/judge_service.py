from app.models.submission import Submission, SubmissionStatus # Đảm bảo import đúng cấu trúc của bạn
from app.models.test_case import TestCase
from app.workers.sandbox_worker import run_python_code
from app.db.session import SessionLocal

def process_submission(submission_id: int):
    # 1. Tự tạo một kết nối Database ĐỘC LẬP cho tiến trình chạy ngầm
    db = SessionLocal()
    try:
        # 2. Tìm bài nộp trong Database
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            print(f"Lỗi: Không tìm thấy bài nộp ID {submission_id}")
            return
            
        # Cập nhật trạng thái đang chấm
        submission.status = SubmissionStatus.JUDGING
        db.commit()

        # 3. Rút hết Test Case của bài tập này ra
        test_cases = db.query(TestCase).filter(TestCase.problem_id == submission.problem_id).all()
        
        if not test_cases:
            submission.status = SubmissionStatus.SYSTEM_ERROR
            submission.error_message = "Bài tập này chưa có Test Case."
            db.commit()
            return

        # 4. Bắt đầu vòng lặp chấm điểm
        all_passed = True
        total_runtime = 0.0 # Cộng dồn thời gian chạy của tất cả test case

        for tc in test_cases:
            # Nhốt code và input vào Hộp cát
            result = run_python_code(submission.source_code, tc.input_data)
            
            total_runtime += result["runtime"]

            # Nếu code bị lỗi cú pháp / sập
            if result["status"] != "Success":
                submission.status = SubmissionStatus.RUNTIME_ERROR
                submission.error_message = result["output"]
                all_passed = False
                break

            # Nếu code chạy được, nhưng kết quả KHÔNG KHỚP đáp án
            if result["output"].strip() != tc.expected_output.strip():
                submission.status = SubmissionStatus.WRONG_ANSWER
                all_passed = False
                break

        # 5. Nếu vượt qua mọi ải Test Case
        if all_passed:
            submission.status = SubmissionStatus.ACCEPTED
            submission.error_message = None
            
        # Lưu tổng thời gian chạy
        submission.runtime = total_runtime

        # 6. Ghi chốt sổ vào MySQL
        db.commit()

    except Exception as e:
        print(f"Lỗi hệ thống khi chấm bài {submission_id}:", e)
        # Nếu có lỗi sập server, cố gắng cập nhật DB
        if 'submission' in locals() and submission:
            submission.status = SubmissionStatus.SYSTEM_ERROR
            submission.error_message = str(e)
            db.commit()
            
    finally:
        # 7. Xong việc thì đóng cửa kết nối (CỰC KỲ QUAN TRỌNG)
        db.close()