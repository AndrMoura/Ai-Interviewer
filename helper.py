import base64
import time
import streamlit as st

from mutagen.mp3 import MP3
from langchain.llms.ollama import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from prompt import question_generator_prompt
from gtts import gTTS


def generate_questions(resume, role, role_description, model_name="llama3.2:1b"):

    question_generator_template = PromptTemplate(
        template=question_generator_prompt,
        input_variables=["role", "description", "resume_text"],
    )

    llm = Ollama(model=model_name)

    question_generator_chain = LLMChain(llm=llm, prompt=question_generator_template)

    guidelines = question_generator_chain.run(
        role=role, description=role_description, resume_text=resume
    )

    return guidelines


def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        placeholder = st.empty()
        md = f"""
            <audio id='audio' autoplay="true" style="display: none">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        placeholder.markdown(
            md,
            unsafe_allow_html=True,
        )


def play_audio(response, file_path):
    tts = gTTS(response)
    tts.save(file_path)
    autoplay_audio(file_path)


def play_audio_block(response, file_path):
    tts = gTTS(response)
    tts.save(file_path)
    audio = MP3(file_path)
    duration = audio.info.length
    autoplay_audio(file_path)
    time.sleep(duration)
