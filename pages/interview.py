import streamlit as st
from datetime import datetime, timedelta
import asyncio
from helper import generate_questions

from helper import autoplay_audio

# Constants
INTERVIEW_DURATION = 5 * 60


def initialize_interview_state():
    if "interview_started" not in st.session_state:
        st.session_state["interview_started"] = True
    if "start_time" not in st.session_state:
        st.session_state["start_time"] = datetime.now()
    if "remaining_time" not in st.session_state:
        st.session_state["remaining_time"] = INTERVIEW_DURATION


async def countdown_timer(timer_placeholder):
    while st.session_state.remaining_time > 0:
        elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds()
        st.session_state.remaining_time = max(0, INTERVIEW_DURATION - int(elapsed_time))

        timer_placeholder.info(
            f"⏳ Time remaining: {str(timedelta(seconds=st.session_state.remaining_time))}"
        )
        if st.session_state.remaining_time <= 0:
            timer_placeholder.warning("⏰ Time's up!")
            # TODO change force interview end
            break
        await asyncio.sleep(1)


mockup_question = "To start, can you tell me a bit about your background and experience"


def main():
    if not st.session_state.get("authentication_status"):
        st.error("Please log in first")
        st.switch_page("app.py")
        return

    autoplay_audio("/home/andre/aiinterviewer/hello.mp3")

    st.title("Interview in Progress 🎯")

    initialize_interview_state()

    timer_placeholder = st.empty()

    with st.chat_message("assistant"):
        st.write("Hello 👋")

    with st.chat_message("user"):
        st.write("Hey ")

    if "interview_questions" in st.session_state:

        # Answer input
        answer = st.text_area("Your answer:", key=f"answer_")

        # Next question button
        if st.button("Next Question"):
            st.session_state["current_question_idx"] += 1
        st.success("Interview Complete! 🎉")
        if st.button("Return to Home"):
            st.session_state["interview_started"] = False
            st.switch_page("app.py")

    if st.session_state.remaining_time > 0:
        asyncio.run(countdown_timer(timer_placeholder))


if __name__ == "__main__":
    main()
