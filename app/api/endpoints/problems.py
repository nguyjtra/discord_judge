from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.problem import Problem
from app.models.test_case import TestCase
from app.models.submission import Submission
from app.schemas.problem import ProblemCreate, ProblemResponse

class TestCaseCreate(BaseModel):
    input_data: str = ""
    expected_output: str

class TestCaseResponse(BaseModel):
    id: int
    problem_id: int
    input_data: str
    expected_output: str

    class Config:
        from_attributes = True

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProblemResponse)
def create_problem(problem_in: ProblemCreate, db: Session = Depends(get_db)):
    new_problem = Problem(**problem_in.model_dump())
    
    db.add(new_problem)
    db.commit()
    db.refresh(new_problem)
    
    return new_problem

@router.get("/", response_model=list[ProblemResponse])
def get_all_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    return problems

@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem_details(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập này!")
        
    return problem

@router.put("/{problem_id}", response_model=ProblemResponse)
def update_problem(problem_id: int, problem_in: ProblemCreate, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập này!")

    for key, value in problem_in.model_dump().items():
        setattr(problem, key, value)

    db.commit()
    db.refresh(problem)
    return problem

@router.delete("/{problem_id}")
def delete_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập này!")

    db.query(TestCase).filter(TestCase.problem_id == problem_id).delete()
    db.query(Submission).filter(Submission.problem_id == problem_id).delete()
    db.delete(problem)
    db.commit()
    return {"message": "Đã xóa bài tập thành công!"}

@router.get("/{problem_id}/test-cases", response_model=list[TestCaseResponse])
def get_problem_test_cases(problem_id: int, db: Session = Depends(get_db)):
    return db.query(TestCase).filter(TestCase.problem_id == problem_id).all()

@router.post("/{problem_id}/test-cases", response_model=TestCaseResponse)
def create_test_case(problem_id: int, tc_in: TestCaseCreate, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập này!")

    new_tc = TestCase(
        problem_id=problem_id,
        input_data=tc_in.input_data,
        expected_output=tc_in.expected_output,
    )
    db.add(new_tc)
    db.commit()
    db.refresh(new_tc)
    return new_tc

@router.delete("/test-cases/{test_case_id}")
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Không tìm thấy test case!")
    db.delete(tc)
    db.commit()
    return {"message": "Đã xóa test case!"}
