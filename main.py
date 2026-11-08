from fastapi import FastAPI
from app.db.session import engine
# Import Base và các bảng để SQLAlchemy "nhận diện" được chúng
from app.models.base import Base
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.ticket import Ticket
app = FastAPI()

@app.on_event("startup")
def startup_db():
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as connection:
            print("🎉  MYSQL success!")
    except Exception as e:
        print("❌ Fail:", e)

@app.get("/")
def hello_world():
    return {"message": "Xin chao! API và Database đã kết nối!"}