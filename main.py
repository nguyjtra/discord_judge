from fastapi import FastAPI
from app.db.session import engine
from app.models.base import Base
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.ticket import Ticket

# 1. THÊM DÒNG IMPORT NÀY:
from app.api.endpoints import problems, submissions
app = FastAPI()

# 2. THÊM DÒNG INCLUDE_ROUTER NÀY (Để ngay dưới app = FastAPI()):
app.include_router(problems.router, prefix="/api/problems", tags=["Problems"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Submissions"])

@app.on_event("startup")
def startup_db():
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as connection:
            print("🎉 MYSQL THÀNH CÔNG!")
    except Exception as e:
        print("❌ Lỗi rồi:", e)

@app.get("/")
def hello_world():
    return {"message": "Xin chao! Database đã sẵn sàng."}