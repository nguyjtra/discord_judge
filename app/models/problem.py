from sqlalchemy import Integer, String, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    time_limit: Mapped[float] = mapped_column(Float, default=1.0)
    memory_limit: Mapped[int] = mapped_column(Integer, default=256)
    difficulty: Mapped[str] = mapped_column(String(50))

    submissions = relationship("Submission", back_populates="problem")