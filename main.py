import re
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text, inspect
from app.db.session import engine
from app.models.base import Base
from app.models.problem import Problem
from app.models.submission import Submission
from app.models.ticket import Ticket
from app.api.endpoints import problems, submissions, tickets

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
FE_DIR = BASE_DIR / "FE"

app.mount("/asset", StaticFiles(directory=str(FE_DIR / "asset")), name="asset")
app.mount("/images", StaticFiles(directory=str(FE_DIR / "asset" / "images")), name="images")

INCLUDE_PATTERN = re.compile(r'<include\s+src=["\']([^"\']+)["\']\s*(?:/>|>\s*</include>)', re.DOTALL)

def render_with_includes(file_path: Path) -> str:
    content = file_path.read_text(encoding="utf-8")
    def replace_include(match: re.Match) -> str:
        rel_src = match.group(1)
        target_path = (file_path.parent / rel_src).resolve()
        if target_path.exists():
            return render_with_includes(target_path)
        return f"<!-- Missing include: {rel_src} -->"
    return INCLUDE_PATTERN.sub(replace_include, content)

app.include_router(problems.router, prefix="/api/problems", tags=["Problems"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["Submissions"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])

@app.on_event("startup")
def startup_db():
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as connection:
            print("🎉 MYSQL THÀNH CÔNG!")
    except Exception as e:
        print("❌ Lỗi rồi:", e)

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard():
    html = render_with_includes(FE_DIR / "templates" / "admin.html")
    return HTMLResponse(content=html)

@app.get("/")
def hello_world():
    return {"message": "Xin chao! Database đã sẵn sàng."}
