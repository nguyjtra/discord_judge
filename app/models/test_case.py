


from sqlalchemy import Column, Integer, Text, ForeignKey
from app.models.base import Base
class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    
    # Khóa ngoại: Test case này dùng để chấm cho Bài tập nào?
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    
    # Dữ liệu bơm vào (Ví dụ: "1 2")
    input_data = Column(Text, default="")
    
    # Kết quả mong đợi (Ví dụ: "3")
    expected_output = Column(Text, nullable=False)