from pydantic import BaseModel
from typing import Optional
# Code này quy định khi tạo 1 đề bài, user bắt buộc phải nhập title, description, difficulty, 
# còn time_limit nếu không nhập sẽ tự mặc định là 1.0.
# Các trường dữ liệu cơ bản
class ProblemBase(BaseModel):
    title: str
    description: str
    time_limit: Optional[float] = 1.0
    memory_limit: Optional[int] = 256
    difficulty: str

# Dữ liệu yêu cầu khi TẠO (POST)
class ProblemCreate(ProblemBase):
    pass

# Dữ liệu trả về (GET) - có thêm cái ID từ database
class ProblemResponse(ProblemBase):
    id: int

    # Dòng này giúp Pydantic hiểu được dữ liệu từ SQLAlchemy
    class Config:
        from_attributes = True