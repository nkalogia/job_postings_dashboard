from pydantic import BaseModel
from typing import List, Optional

class Text(BaseModel):
    data: str

class Task(BaseModel):
    task_id: str
    status: str

class Prediction(BaseModel):
    task_id: str
    status: str
    skills: Optional[List[str]]