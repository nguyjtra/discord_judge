from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Import các thành phần chúng ta đã viết
from app.db.session import SessionLocal
from app.models.problem import Problem
from app.schemas.problem import ProblemCreate, ProblemResponse

router = APIRouter()

# Hàm mở cửa kết nối Database cho mỗi lần có người gọi API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # Gọi xong phải đóng cửa lại cho khỏi tràn RAM

# 1. API: Thêm một đề bài mới (Method: POST)
@router.post("/", response_model=ProblemResponse)
def create_problem(problem_in: ProblemCreate, db: Session = Depends(get_db)):
    # problem_in.model_dump() sẽ biến dữ liệu user gửi thành một Dictionary
    new_problem = Problem(**problem_in.model_dump())
    
    db.add(new_problem)   # Thêm vào phiên làm việc
    db.commit()           # Xác nhận lưu thẳng vào MySQL
    db.refresh(new_problem) # Lấy lại ID vừa được MySQL tạo tự động
    
    return new_problem

# 2. API: Lấy danh sách tất cả đề bài (Method: GET)
@router.get("/", response_model=list[ProblemResponse])
def get_all_problems(db: Session = Depends(get_db)):
    # Lấy tất cả các dòng trong bảng Problem
    problems = db.query(Problem).all()
    return problems


@router.get("/{problem_id}", response_model=ProblemResponse)
def get_problem_details(problem_id: int, db: Session = Depends(get_db)):
    # Tìm bài tập có ID khớp với yêu cầu
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài tập này!")
        
    return problem