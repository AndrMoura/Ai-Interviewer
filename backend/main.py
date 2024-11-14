import os
import io
import json
import jwt
import base64
import uuid
import asyncio
import pickle

from pydub import AudioSegment
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Form, File, UploadFile
from .audio import TextToAudio, AudioToText
from .chat_model import InterViewer, generate_questions, evaluate_interview
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import InterviewSettings
from .session import SessionManager
from .util import save_interview, save_dict, resume_reader
from .jd import ROLE_CFG

SAVE_DIR = "saved_audio"
os.makedirs(SAVE_DIR, exist_ok=True)
app = FastAPI()

origins = [
    "http://localhost:3000",
]

def initialize_tts_stt():
    """Initialize the Text-to-Speech model."""
    tts = TextToAudio()
    stt = AudioToText('tiny')
    return tts, stt

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mock database
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "password": "password123",  # Plain text password for testing
        "role": "user" 
    },
    "adminuser": {
        "username": "adminuser",
        "password": "adminpassword",
        "role": "admin"
    }
}
# Mock InterViews
interview_settings_db = {}
rated_interviews_db = []
tts, stt = initialize_tts_stt()

# add a mock interview
for k, v in ROLE_CFG.items():
    interview_settings_db[k] = {
        "customQuestions": "Ask about his favorite programming language\nAsk about his cat or dog!",
        'jobDescription': v
    }

# add rated_interviews
try:
    with open("test_data.pkl", 'rb') as file:
        rated_interviews_db = pickle.load(file)
except FileNotFoundError:
    rated_interviews_db = []

session_manager = SessionManager()

# Function to save the accumulated audio buffer to a WebM file
async def save_audio_buffer_to_file(buffer):
    """Save the accumulated audio buffer to a WebM file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        webm_file_path = os.path.join(SAVE_DIR, f"recording_{timestamp}.ogg")

        with open(webm_file_path, "wb") as webm_file:
            webm_file.write(buffer.getvalue())
        
        return webm_file_path

    except Exception as e:
        print(f"Error saving audio to WebM: {e}")
        return None

    finally:
        buffer.seek(0)
        buffer.truncate(0)

def generate_ogg_response(tts, text, ref_audio, output_path="question.wav") -> io.BytesIO:
    """Generate OGG audio from text using TTS and return as a BytesIO buffer."""
    tts.generate_audio_response(text, ref_audio=ref_audio, file_path=output_path)
    audio = AudioSegment.from_wav(output_path)
    ogg_audio_buffer = io.BytesIO()
    audio.export(ogg_audio_buffer, format="ogg")
    ogg_audio_buffer.seek(0)
    return ogg_audio_buffer

async def process_interview_data(interviewer: InterViewer, session_id):
    """Process the interview data asynchronously (e.g., save, evaluate, etc.)"""
    print("Starting task to evaluate")
    try:
        interview = save_interview(interviewer.memory.chat_memory.messages, session_id)
        evaluation = evaluate_interview(interview, role=interviewer.role, role_description=interviewer.role_description)
        interview['evaluation'] = evaluation
        print('interview', interview)
        save_dict(interview, 'test_data.pkl')
        
        print("Interview data saved and evaluated.")
    except Exception as e:
        print(f"Error during interview processing: {e}")

async def handle_websocket_audio_stream(websocket: WebSocket, buffer, interviewer: InterViewer, stt, tts, session_id):
    """Handle the WebSocket audio streaming and save when done."""
    try:
        data = await websocket.receive()

        if "bytes" in data:
            buffer.write(data["bytes"])
        elif "text" in data:
            message = json.loads(data["text"])
            if message.get("endOfMessage"):
                webm_file_path = await save_audio_buffer_to_file(buffer)
                user_ans = stt.transcribe_audio(webm_file_path)
                print("user_ans", user_ans)
                if webm_file_path:
                    model_question = interviewer.generate_question(user_response=user_ans)
                    ogg_audio_buffer = generate_ogg_response(tts, model_question, ref_audio='sample.wav')
                    await websocket.send_bytes(ogg_audio_buffer.read())
                    print("Sent OGG audio response.")
                else:
                    print("Failed to save audio.")
            if message.get("end_interview"):
                print("end_interview_requested")
                asyncio.create_task(process_interview_data(interviewer, session_id))
                await websocket.send_text("Interview ended successfully.")
                await websocket.close()                 
                return True
    except WebSocketDisconnect:
        print("Cleaning up")

@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    session_id = None
    data = await websocket.receive()
    if "text" in data:
        message = json.loads(data["text"])
        if "session_id" in message:
            session_id = message.get("session_id")

    interviewer = session_manager.get_session(session_id)
    if not interviewer:
        print("Interviewer not found")
        await websocket.close()
        return

    audio_buffer = io.BytesIO()  # Buffer for incoming audio data

    try:
        while True:
            to_break = await handle_websocket_audio_stream(
                websocket,
                audio_buffer,
                interviewer,
                stt,
                tts,
                session_id,
            )
            if to_break:
                session_manager.remove_session(session_id)
                break

    except WebSocketDisconnect:
        session_manager.remove_session(session_id)


## LOGIN
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Utility function to authenticate user
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user['password']):
        return False
    return user


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user with form_data.username and form_data.password
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    token = create_access_token(data={"sub": user['username'], "role": user['role']})
    return JSONResponse(content={"message": "Login successful", "token": token, "role": user['role']})


@app.post("/start-interview")
async def start_interview(
    role: str = Form(...),
    roleDescription: str = Form(...),
    portfolio_text: str = Form(None),
    portfolio_file: UploadFile = File(None),
):
    if portfolio_text:
        resume_text = portfolio_text
    elif portfolio_file:
        try:
            pdf_content = await portfolio_file.read()
            resume_text = resume_reader(pdf_content)
        except Exception as e:
            return JSONResponse(status_code=400, content={"detail": f"Error reading PDF: {str(e)}"})

    customQuestions = interview_settings_db.get(role, {}).get('customQuestions', [])
    # guidelines = generate_questions(
    #     resume=resume_text,  # Use the text if provided
    #     role=role,
    #     role_description=roleDescription,
    #     must_have_questions=customQuestions,
    # )
    session_id = str(uuid.uuid4())
    interviewer = InterViewer("gpt-4o-mini",
                              'guidelines',
                              name='Anna',
                              role=role,
                              resume=resume_text,
                              role_description=roleDescription)
    # first_question = interviewer.generate_question("ask a question")
    # interviewer.memory.clear()
    # interviewer.memory.chat_memory.add_ai_message(first_question)
    first_question = 'Hi Im Anna welcome, what is your name?'
    buffer = generate_ogg_response(
        tts=tts,
        text=first_question,
        ref_audio='../sample.wav',
        output_path='output.wav'
    )

    session_manager.create_session(
        session_id=session_id,
        model=interviewer,
    )

    audio_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return JSONResponse(content={
        "audio_base64": audio_base64,
        "session_id": session_id
    })
    


@app.get("/interviews/")
async def get_interview_summaries():
    print("rated_interview", rated_interviews_db)
    summaries = [
        {
            'session_id': interview['session_id'],
            'preview': interview['messages'][0]['message'][:50]
        }
        for interview in rated_interviews_db
    ]
    print("summaries", summaries)
    return JSONResponse(content=summaries)

@app.get("/interviews/{session_id}")
async def get_interview_detail(session_id: str):
    interview = next((i for i in rated_interviews_db if i['session_id'] == session_id), None)
    if interview is None:
        return JSONResponse(status_code=404, content={"message": "Interview not found"})
    
    return JSONResponse(content=interview)

@app.post("/admin/interview-settings")
async def save_interview_settings(settings: InterviewSettings):
    interview_settings_db[settings.role] = {
        "customQuestions": settings.customQuestions,
        "jobDescription": settings.jobDescription
    }

    return {"message": "Interview settings saved successfully"}

@app.get("/roles")
async def get_roles():
    roles_with_description = [
        {"role": role, "jobDescription": interview_settings_db.get(role, {}).get("jobDescription", "No description available")}
        for role in interview_settings_db.keys()
    ]
    return {"roles": roles_with_description}

@app.delete("/delete_session/{session_id}")
async def delete_session(session_id: str):
    try:
        print(session_manager.sessions)
        session_manager.remove_session(session_id)
        return {"message": f"Session {session_id} deleted successfully."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
