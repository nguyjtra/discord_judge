from fastapi import FastAPI
from app.db.session import engine
app = FastAPI()

@app.on_event("startup")
def startup_db():
    try:
        with engine.connect() as connection:
            print("🎉  MYSQL success!")
    except Exception as e:
        print("❌ Fail:", e)

@app.get("/")
def hello_world():
    return {"message": "Xin chao! API và Database đã kết nối!"}