import streamlit as st
import datetime
from helper import play_audio, play_audio_block
from streamlit_mic_recorder import mic_recorder
from audio_recorder_streamlit import audio_recorder
from audiorecorder import audiorecorder
from pydub import AudioSegment
from audio import AudioToText

audio_path = "answer_temp.wav"

st.title("Interview in Progress 🎯")

audio_to_text = AudioToText("small")

if "messages" not in st.session_state:
    st.session_state.messages = []


def get_now_date():
    return datetime.datetime.now().replace(microsecond=0)


def direct_text_prompt():
    """Render and return the user's input."""
    placeholder = f"Answer your interviewer"

    with st.container():
        left, right = st.columns([300, 145])
        with left:
            text_from_chat_input_widget = st.chat_input(placeholder=placeholder)
        with right:
            text_audio_recorder = widget_mic_recorder()
            # saved_path = audio_to_text.save_audio(text_audio_recorder, audio_path)
            # text_audio = audio_to_text.transcribe_audio(saved_path)
            text_audio = "ok"

    return text_from_chat_input_widget or text_audio


def widget_mic_recorder() -> AudioSegment:
    """Record audio from the microphone."""
    red_square = "\U0001F7E5"
    microphone = "\U0001F3A4"
    play_button = "\U000025B6"

    recording = mic_recorder(
        key=f"audiorecorder_widget_",
        start_prompt=play_button + microphone,
        stop_prompt=red_square,
        just_once=True,
        use_container_width=True,
        format="wav",
    )
    if recording is None:
        return AudioSegment.silent(duration=0)

    return AudioSegment(
        data=recording["bytes"],
        sample_width=recording["sample_width"],
        frame_rate=recording["sample_rate"],
        channels=1,
    )

    # audio = audiorecorder("", "", True, "test_key"), 


chat_msgs_container = st.container(height=550, border=False)
with chat_msgs_container:
    with st.chat_message("assistant"):
        st.caption(get_now_date())
        st.markdown("greetings sons of bitches")


with chat_msgs_container:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.caption(message["timestamp"])
            st.markdown(message["content"])


prompt = direct_text_prompt()
with chat_msgs_container:
    if prompt:
        time_now = get_now_date()
        # Display user message in chat message container
        with st.chat_message("user"):
            st.caption(time_now)
            st.markdown(prompt)
            st.session_state.messages.append(
                {"role": "user", "timestamp": time_now, "content": prompt}
            )

        with st.chat_message("assistant"):
            test_res = prompt
            time_now = get_now_date()
            text_reply_container = st.empty()
            text_reply_container.caption(time_now)
            text_reply_container.markdown(test_res)
            st.session_state.messages.append(
                {"role": "assistant", "timestamp": time_now, "content": test_res}
            )

# if prompt := st.chat_input(""):
#     st.chat_message("user").markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     response = f"Echo: {prompt}"
#     # play_audio(response, temporary_audio)
#     with st.chat_message("assistant"):
#         st.markdown(response)

#     st.session_state.messages.append({"role": "assistant", "content": response})


# if not st.session_state.get("ongoing_interview"):
#     init_question = "Hello and welcome"

#     with st.chat_message("assistant"):
#         st.caption("test")
#         st.markdown(init_question)
#         st.session_state.ongoing_interview = True

#     play_audio_block(init_question, temporary_audio)
#     st.session_state.messages.append({"role": "assistant", "content": init_question})


# audio_bytes = audio_recorder(auto_start=True, pause_threshold=1)
