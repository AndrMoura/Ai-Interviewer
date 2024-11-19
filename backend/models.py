from pydantic import BaseModel
from typing import Optional

class LoginModel(BaseModel):
    username: str
    password: str


class InterviewSettings(BaseModel):
    role: str
    customQuestions: str
    jobDescription: str

class RoleData(BaseModel):
    custom_questions: Optional[str] = None
    job_description: Optional[str] = None