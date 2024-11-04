import streamlit as st
import datetime
import tempfile
import base64
import soundfile as sf

from audiorecorder import audiorecorder
from audio import AudioToText, TextToAudio
from helper import autoplay_audio_from_array


st.title("Interview in Progress 🎯")


@st.cache_resource
def load_TTS(model_name):
    return AudioToText(model_name)


@st.cache_resource
def load_STT(model_name):
    return TextToAudio(model_name=model_name, device="cuda:0")


tts = load_TTS("small")
stt = load_STT("hf://SWivid/F5-TTS/F5TTS_Base/model_1200000.safetensors")

audio_path = "answer_temp.wav"
audio_ref_path = "sample.wav"

if "messages" not in st.session_state:
    st.session_state.messages = []


def get_now_date():
    return datetime.datetime.now().replace(microsecond=0)


def direct_text_prompt():
    """Render and return the user's input."""

    with st.container():
        left, right = st.columns([0.2, 0.8])
        with st.spinner(""):
            with left:
                pass
            with right:
                text_audio_recorder = audiorecorder("", "", True, "audio_recorder")
                saved_path = tts.save_audio(text_audio_recorder, audio_path)
                text_audio = tts.transcribe_audio(saved_path)

    return text_audio


def display_message(role, content):
    """Display a chat message for a given role ('user' or 'assistant') with a timestamp."""
    time_now = get_now_date()
    with st.chat_message(role):
        st.caption(time_now)
        st.markdown(content)

    st.session_state.messages.append(
        {"role": role, "timestamp": time_now, "content": content}
    )


chat_msgs_container = st.container(height=550, border=False)
with chat_msgs_container:
    with st.chat_message("assistant"):
        intro_text = 'greetings sons of bitches'
        st.caption(get_now_date())
        st.markdown(intro_text)
        
        response = stt.generate_audio_response(
            ai_response=intro_text,
            ref_audio=audio_ref_path,
            ref_text="",
            remove_silence=True,
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.caption(message["timestamp"])
            st.markdown(message["content"])


prompt = direct_text_prompt()

with chat_msgs_container:
    if prompt:
        display_message("user", prompt)

        response = stt.generate_audio_response(
            ai_response=prompt,
            ref_audio=audio_ref_path,
            ref_text="",
            remove_silence=True,
        )
        print("response", response)
        autoplay_audio_from_array(
            response["wave_data"], response["sample_rate"], response["duration"]
        )
        display_message("assistant", prompt)
