import os
import io
import json
import base64
import uuid
import logging
import asyncio
import soundfile as sf
from datetime import datetime
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    Form,
    File,
    UploadFile,
)
from .audio import TextToAudio, AudioToText
from .chat_model import InterViewer, generate_questions, evaluate_interview
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import RoleSettings, RoleData
from .session import SessionManager
from .util import transform_interview, resume_reader
from .constants import (
    SAVE_DIR,
    SECRET_KEY,
    STT_MODEL,
    INTERVIEW_NAME,
)
from .login import authenticate_user, create_access_token
from kokoro import KPipeline
from .db import (
    get_roles_db,
    create_role_to_db,
    get_interviews_from_db,
    get_role_settings,
    get_role_details_db,
    update_role_details_db,
    save_interview_to_db,
    get_interview_detail_from_db,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("TTS").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

os.makedirs(SAVE_DIR, exist_ok=True)
app = FastAPI()

origins = [
    "http://localhost:3000",
]


def initialize_tts_stt():
    """Initialize the Text-to-Speech model."""
    stt = AudioToText(STT_MODEL)
    tts = KPipeline(lang_code='a')
    return tts, stt


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tts, stt = initialize_tts_stt()
session_manager = SessionManager()


async def save_audio_buffer_to_file(buffer):
    """Save the accumulated audio buffer to a WebM file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        webm_file_path = os.path.join(SAVE_DIR, f"recording_{timestamp}.ogg")

        with open(webm_file_path, "wb") as webm_file:
            webm_file.write(buffer.getvalue())

        return webm_file_path

    except Exception as e:
        logger.error(f"Error saving audio buffer to file: {e}")
        return None
    finally:
        buffer.seek(0)
        buffer.truncate(0)

async def generate_audio_response(tts, text) -> io.BytesIO:
    """
    Generate an audio response from text using TTS and return as a BytesIO buffer.
    """
    def _generate():
        gen = tts(text, voice="af_heart", speed=1.0)
        audio = next(gen).audio

        buffer = io.BytesIO()
        sf.write(buffer, audio, samplerate=24000, format="WAV")
        buffer.seek(0)
        return buffer

    return await asyncio.to_thread(_generate)


async def process_interview_data(interviewer: InterViewer, session_id):
    """Save interview to db"""
    try:
        logger.info("Processing interview data")
        interview = transform_interview(interviewer.memory.chat_memory.messages)
        evaluation = await evaluate_interview(
            interview,
            role=interviewer.role,
            role_description=interviewer.role_description,
        )
        save_interview_to_db(
            session_id=session_id,
            role=interviewer.role,
            role_description=interviewer.role_description,
            messages=interview,
            evaluation=evaluation,
        )
        logger.info("Interview data saved to db")
    except Exception as e:
        logger.error(f"Error during interview processing: {e}")


async def handle_websocket_audio_stream(
    websocket: WebSocket,
    buffer: io.BytesIO,
    interviewer: InterViewer,
    stt: AudioToText,
    tts: TextToAudio,
    session_id,
):
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
                logger.info(f"User answer: {user_ans}")
                if webm_file_path:
                    model_question = await interviewer.generate_question(user_response=user_ans)
                    ogg_audio_buffer = await generate_audio_response(
                        tts, model_question
                    )
                    await websocket.send_bytes(ogg_audio_buffer.read())
                    logger.info("Sent audio response.")
                else:
                    logger.error("Failed to save audio.")
            if message.get("end_interview"):
                asyncio.create_task(process_interview_data(interviewer, session_id))
                await websocket.send_text("Interview ended successfully.")
                await websocket.close()
                buffer.close()
                return True
    except WebSocketDisconnect:
        buffer.close()
    except RuntimeError as e:
        logger.error(f"Caught a RuntimeError: {e}")
        buffer.close()
        return True


@app.websocket("/ws/audio")
async def audio_stream(websocket: WebSocket):
    interviewer = None
    await websocket.accept()
    session_id = None
    data = await websocket.receive()
    if "text" in data:
        message = json.loads(data["text"])
        if "session_id" in message:
            session_id = message.get("session_id")

    stored_data = session_manager.get_session(session_id)
    if not stored_data:
        logger.error("Interviewer not found")
        await websocket.close()
        return
    else:
        interviewer = InterViewer.from_dict(stored_data)

    audio_buffer = io.BytesIO()

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


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, secret_key=SECRET_KEY
    )
    return JSONResponse(
        content={"message": "Login successful", "token": token, "role": user["role"]}
    )


@app.post("/start-interview")
async def start_interview(
    role: str = Form(...),
    role_description: str = Form(...),
    portfolio_text: str = Form(None),
    portfolio_file: UploadFile = File(None),
):
    try:
        if portfolio_text:
            resume_text = portfolio_text
        elif portfolio_file:
            try:
                pdf_content = await portfolio_file.read()
                resume_text = resume_reader(pdf_content)
            except Exception as e:
                return JSONResponse(
                    status_code=400, content={"detail": f"Error reading PDF: {str(e)}"}
                )
        custom_questions, _ = get_role_settings(role)
        must_have_questions = (custom_questions.split("\n") if custom_questions else [],)

        guidelines = await generate_questions(
            resume=resume_text,
            role=role,
            role_description=role_description,
        )
        session_id = str(uuid.uuid4())
        interviewer = InterViewer(
            guidelines,
            INTERVIEW_NAME,
            role,
            resume_text,
            role_description,
            must_have_questions,
        )
        first_question = await interviewer.generate_question("ask a question")
        interviewer.memory.clear()
        interviewer.memory.chat_memory.add_ai_message(first_question)
        buffer = await generate_audio_response(tts, first_question)
        session_manager.create_session(session_id, interviewer.to_dict())
        audio_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return JSONResponse(content={"audio_base64": audio_base64, "session_id": session_id})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": f"Unexpected error: {str(e)}"})


@app.get("/interviews/")
async def get_interview_summaries():
    interviews = get_interviews_from_db()
    for interview in interviews:
        interview["preview"] = interview["messages"][0]["message"][:50]
        interview.pop("messages")

    return JSONResponse(content=interviews)


@app.get("/interviews/{session_id}")
async def get_interview_detail(session_id: str):
    interview = get_interview_detail_from_db(session_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return JSONResponse(content=interview)


@app.post("/admin/create-role")
async def save_interview_settings(settings: RoleSettings):
    try:
        create_role_to_db(
            role=settings.role,
            custom_questions=settings.customQuestions,
            job_description=settings.jobDescription,
        )
        return {"message": "Interview settings saved successfully"}
    except ValueError as e:
        logger.error(f"Error saving interview settings: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/admin/roles")
async def get_roles():
    return {"roles": await get_roles_db()}


@app.get("/admin/roles/{role}")
async def get_role_details(role: str):
    """
    Fetch the details of a specific role by its name.
    """
    try:
        role_details = await get_role_details_db(role)
        if not role_details:
            raise HTTPException(status_code=404, detail="Role not found")
        return role_details
    except Exception as e:
        logger.error(f"Error fetching role details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching role details: {str(e)}")


@app.put("/admin/roles/{role}")
async def update_role(role: str, role_data: RoleData):
    """
    Update the details of a specific role.
    """
    try:
        updated_role = await update_role_details_db(role, role_data.model_dump())
        if not updated_role:
            raise HTTPException(status_code=404, detail="Role not found")
        return {"message": "Role updated successfully"}
    except Exception as e:
        logger.error(f"Error updating role: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating role: {str(e)}")


@app.delete("/delete_session/{session_id}")
async def delete_session(session_id: str):
    try:
        session_manager.remove_session(session_id)
        return {"message": f"Session {session_id} deleted successfully."}
    except ValueError as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
