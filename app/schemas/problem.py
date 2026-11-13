from pydantic import BaseModel
from typing import Optional

class ProblemBase(BaseModel):
    title: str
    description: str
    time_limit: Optional[float] = 1.0
    memory_limit: Optional[int] = 256
    difficulty: str

class ProblemCreate(ProblemBase):
    pass

class ProblemResponse(ProblemBase):
    id: int

    class Config:
        from_attributes = True
