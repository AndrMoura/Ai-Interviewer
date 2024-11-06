import streamlit as st
import datetime
import time
import threading


from audiorecorder import audiorecorder
from audio import AudioToText, TextToAudio
from helper import autoplay_audio_from_array
from chat_model import InterViewer
from datetime import timedelta
from functools import wraps

INTERVIEW_DURATION = 10 * 60


def run_in_thread(func):
    from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        ctx = get_script_run_ctx()
        add_script_run_ctx(thread, ctx)
        thread.start()

    return wrapper


# FIX THIS - Must end thread when leaving the page
@run_in_thread
def countdown_timer(timer_placeholder):
    print("Spawning new thread")
    while st.session_state.get("remaining_time", INTERVIEW_DURATION) > 0:
        elapsed_time = (
            datetime.datetime.now() - st.session_state.start_time
        ).total_seconds()
        st.session_state.remaining_time = max(0, INTERVIEW_DURATION - int(elapsed_time))

        timer_placeholder.info(
            f"⏳ Time remaining: {str(timedelta(seconds=st.session_state.remaining_time))}"
        )
        if st.session_state.remaining_time <= 0:
            timer_placeholder.warning("⏰ Time's up!")
            st.session_state.interview_end = True

        time.sleep(1)
    print("Ended")


with st.spinner("Loading your interview..."):

    @st.cache_resource
    def load_TTS(model_name):
        return AudioToText(model_name)

    @st.cache_resource
    def load_STT():
        return TextToAudio()

    @st.cache_resource
    def load_interviewer(model_name="llama3.2:3b"):
        if st.session_state.get("questions"):
            return InterViewer(
                model_name=model_name, questions=st.session_state.questions
            )
        else:
            print("loading mock guidelines")
            return InterViewer(model_name=model_name, questions="Hello who are you")


tts = load_TTS("small")
stt = load_STT()
interviewer = load_interviewer()
audio_path = "answer_temp.wav"
audio_ref_path = "sample.wav"


def get_now_date():
    return datetime.datetime.now().replace(microsecond=0)


def direct_text_prompt():
    """Render and return the user's input."""
    text_audio = ""

    if "audio_recorder_key" not in st.session_state:
        st.session_state.audio_recorder_key = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

    with st.container():
        left, right = st.columns([0.2, 0.8])
        with st.spinner(""):
            with left:
                pass
            with right:
                # Workaround - audiorecorder always reruns the PREVIOUS audio.
                # We set a key to create another "instance" of the audio recorder
                text_audio_recorder = audiorecorder(
                    "",
                    "",
                    True,
                    key=f"audio_recorder_{st.session_state.audio_recorder_key}",
                )
                if len(text_audio_recorder) > 0:
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


def initialize_chat_session():
    if "initial_audio_played" not in st.session_state:
        st.session_state.initial_audio_played = False

        if not len(st.session_state.messages):
            content = interviewer.first_question
            timestamp = get_now_date()

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "timestamp": timestamp,
                    "content": content,
                }
            )

            with st.chat_message("assistant"):
                st.caption(timestamp)
                st.markdown(content)

            if not st.session_state.initial_audio_played:
                response = stt.generate_audio_response(
                    ai_response=content,
                    ref_audio=audio_ref_path,
                )
                autoplay_audio_from_array(
                    response["wave_data"], response["sample_rate"], response["duration"]
                )

                st.session_state.initial_audio_played = True

    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.caption(message["timestamp"])
                st.markdown(message["content"])


def initialize_interview_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.datetime.now()

    if "remaining_time" not in st.session_state:
        st.session_state["remaining_time"] = INTERVIEW_DURATION

    if "timer_running" not in st.session_state:
        st.session_state["timer_running"] = False

    if "interview_end" not in st.session_state:
        st.session_state["interview_end"] = False


def reset_state():
    keys_to_clear = [
        "initial_audio_played",
        "messages",
        "start_time",
        "audio_recorder_key",
        "timer_running",
        "interview_end",
    ]
    st.session_state["remaining_time"] = INTERVIEW_DURATION
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.audio_recorder_key = datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )


def main():
    st.session_state.reset = False
    timer_placeholder = st.empty()
    st.title("Interview in Progress 🎯")
    initialize_interview_state()
    timer_placeholder.info(
        f"⏳ Time remaining: {str(timedelta(seconds=st.session_state.remaining_time))}"
    )
    chat_msgs_container = st.container(height=400, border=False, key="chat_container")

    with chat_msgs_container:
        initialize_chat_session()

    prompt = direct_text_prompt()
    with chat_msgs_container:
        if prompt:
            display_message("user", prompt)
            ai_question = interviewer.generate_question(prompt)
            response = stt.generate_audio_response(
                ai_response=ai_question,
                ref_audio=audio_ref_path,
            )
            display_message("assistant", ai_question)
            autoplay_audio_from_array(
                response["wave_data"], response["sample_rate"], response["duration"]
            )

    st.divider()

    left, mid, right = st.columns(3)

    with left:
        if left.button(
            "Main menu",
            help="returns to the main page an stops the interview",
            type="secondary",
        ):
            reset_state()
            st.switch_page("app.py")

    with mid:
        mid.button(
            icon="🔄",
            help="restart your interview",
            label="Restart",
            on_click=reset_state,
        )

    with right:
        if right.button(
            "Stop Interview", help="stops the interview for scoring", type="primary"
        ):
            st.switch_page("pages/evaluation.py")

    if not st.session_state.timer_running:
        countdown_timer(timer_placeholder)
        st.session_state.timer_running = True

    if st.session_state.interview_end:
        st.switch_page("pages/evaluation.py")


if __name__ == "__main__":
    main()
