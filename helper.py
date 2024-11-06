import base64
import time
import streamlit as st
import tempfile
import soundfile as sf

from langchain.llms.ollama import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from prompt import question_generator_prompt


def generate_questions(
    resume, role, role_description, must_have_questions, model_name="llama3.2:3b"
):

    question_generator_template = PromptTemplate(
        template=question_generator_prompt,
        input_variables=["role", "description", "must_have_questions" "resume_text"],
    )

    llm = Ollama(model=model_name)

    question_generator_chain = LLMChain(llm=llm, prompt=question_generator_template)

    guidelines = question_generator_chain.run(
        role=role,
        description=role_description,
        must_have_questions=must_have_questions,
        resume_text=resume,
    )

    return guidelines


def autoplay_audio_from_array(audio_array, sample_rate, duration):

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        # Save numpy array as a wav file
        sf.write(temp_audio_file.name, audio_array, sample_rate)

        # Read the temp file in binary mode to convert to base64
        with open(temp_audio_file.name, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()

        # Streamlit HTML to autoplay the audio
        placeholder = st.empty()
        audio_html = f"""
            <audio autoplay="true" style="display:none;">
                <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
        """
        placeholder.markdown(audio_html, unsafe_allow_html=True)
        time.sleep(duration)
