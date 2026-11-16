from app.models.submission import Submission, SubmissionStatus
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.workers.sandbox_worker import run_python_code
from app.db.session import SessionLocal

def process_submission(submission_id: int):
    db = SessionLocal()
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            print(f"Submission #{submission_id} not found")
            return
            
        submission.status = SubmissionStatus.JUDGING
        db.commit()

        problem = db.query(Problem).filter(Problem.id == submission.problem_id).first()
        time_limit = problem.time_limit if (problem and problem.time_limit) else 2.0
        memory_limit = f"{problem.memory_limit}m" if (problem and problem.memory_limit) else "256m"

        test_cases = db.query(TestCase).filter(TestCase.problem_id == submission.problem_id).all()
        
        if not test_cases:
            submission.status = SubmissionStatus.SYSTEM_ERROR
            submission.error_message = "No test cases configured for this problem."
            db.commit()
            return

        all_passed = True
        total_runtime = 0.0

        for tc in test_cases:
            result = run_python_code(
                source_code=submission.source_code,
                input_data=tc.input_data,
                time_limit=time_limit,
                memory_limit=memory_limit
            )
            
            total_runtime += result["runtime"]

            if result["status"] == "TLE":
                submission.status = SubmissionStatus.TIME_LIMIT_EXCEEDED
                submission.error_message = result["output"]
                all_passed = False
                break

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
            
        submission.runtime = round(total_runtime, 3)
        db.commit()

    except Exception as e:
        print(f"SERVER ERROR {submission_id}:", e)
        if 'submission' in locals() and submission:
            submission.status = SubmissionStatus.SYSTEM_ERROR
            submission.error_message = str(e)
            db.commit()
            
    finally:
        db.close()
