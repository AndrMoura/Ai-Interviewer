from pydantic import BaseModel

class LoginModel(BaseModel):
    username: str
    password: str
    
class InterviewSettings(BaseModel):
    role: str
    customQuestions: str
    jobDescription: str
