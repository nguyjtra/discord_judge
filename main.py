from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Xin chao! FastAPI cua toi da chay thanh cong tren Mac!"}