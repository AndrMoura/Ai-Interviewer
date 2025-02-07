import os

DATABASE_NAME = os.environ.get("DATABASE_NAME", "app.db")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
SECRET_KEY = os.environ.get("SECRET_KEY", "your_default_secret_key")

OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-pro-exp-02-05")

INTERVIEW_MODEL = (
    os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini") 
    if os.environ.get("OPENAI_API_KEY") 
    else os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-pro-exp-02-05")
)
INTERVIEW_NAME = os.environ.get("STT_MODEL", "Anna")
STT_MODEL = os.environ.get("STT_MODEL", "tiny")
TTS_MODEL = os.environ.get("TTS_MODEL", "tts_models/en/ljspeech/tacotron2-DDC")

# if multilingual specify 'en' or 'fr'
MULTILINGUAL_STT = os.environ.get("MULTILINGUAL_STT", False)  # if multilingual specify 'en' or 'fr'

SAVE_DIR = "saved_audio"

ROLE_CFG = {
    "Python (Django) Developer": "Qualifications Bachelor's degree in Computer Science or related field 5+ Years of Software Development Experience Professional experience with Python [Django experience preferred] Professional experience with JavaScript is preferred [React/Redux experience preferred] Experience with Python, Django, Agile development, and APIs Strong understanding of software design patterns and principles Experience with database design and development Excellent problem-solving skills Strong communication skills Strong fundamental understanding and usage of a RDBMS [Postgres preferred] In-depth knowledge and hands on experience with AWS [Terraform experience preferred] Responsibilities End-to-end feature development Refining the SDLC & CI/CD pipelines Maintaining our AWS infrastructure Develop object-oriented Python and Django scripts and protocols, while leveraging tools such as nginx, dnsmasq, and other technologies Build and and deploy applications within an AWS environment"
}
