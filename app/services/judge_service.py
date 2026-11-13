from app.models.submission import Submission, SubmissionStatus
from app.models.test_case import TestCase
from app.workers.sandbox_worker import run_python_code
from app.db.session import SessionLocal

def process_submission(submission_id: int):
    db = SessionLocal()
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            print(f"ERROR {submission_id}")
            return
            
        submission.status = SubmissionStatus.JUDGING
        db.commit()

        test_cases = db.query(TestCase).filter(TestCase.problem_id == submission.problem_id).all()
        
        if not test_cases:
            submission.status = SubmissionStatus.SYSTEM_ERROR
            submission.error_message = "ERROR"
            db.commit()
            return

        all_passed = True
        total_runtime = 0.0

        for tc in test_cases:
            result = run_python_code(submission.source_code, tc.input_data)
            
            total_runtime += result["runtime"]

            if result["status"] != "Success":
                submission.status = SubmissionStatus.RUNTIME_ERROR
                submission.error_message = result["output"]
                all_passed = False
                break

            if result["output"].strip() != tc.expected_output.strip():
                submission.status = SubmissionStatus.WRONG_ANSWER
                submission.error_message = (
                    f"Wrong Answer!\n"
                    f"- Input: {tc.input_data}\n"
                    f"- Your Output: {result['output'].strip()}\n"
                    f"- Expected Output: {tc.expected_output.strip()}"
                )
                all_passed = False
                break

        if all_passed:
            submission.status = SubmissionStatus.ACCEPTED
            submission.error_message = None
            
        submission.runtime = total_runtime
        db.commit()

    except Exception as e:
        print(f"SEVER ERROR {submission_id}:", e)
        if 'submission' in locals() and submission:
            submission.status = SubmissionStatus.SYSTEM_ERROR
            submission.error_message = str(e)
            db.commit()
            
    finally:
        db.close()
