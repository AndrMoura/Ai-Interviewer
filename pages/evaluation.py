import streamlit as st
import threading
import time
import datetime
from datetime import timedelta
from functools import wraps
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

# Constants
INTERVIEW_DURATION = 60

def run_in_thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        ctx = get_script_run_ctx()  
        add_script_run_ctx(thread, ctx)
        thread.start()
    return wrapper

@run_in_thread
def countdown_timer(timer_placeholder):
    print("Spawning new thread", st.session_state.get('remaining_time', INTERVIEW_DURATION))
    while st.session_state.get('remaining_time', INTERVIEW_DURATION) > 0:
        elapsed_time = (datetime.datetime.now() - st.session_state.start_time).total_seconds()
        st.session_state.remaining_time = max(0, INTERVIEW_DURATION - int(elapsed_time))
        timer_placeholder.info(
            f"⏳ Time remaining: {str(timedelta(seconds=st.session_state.remaining_time))}"
        )
        if st.session_state.remaining_time <= 0:
            timer_placeholder.warning("⏰ Time's up!")
            break  # Exit the loop if time is up
        
        time.sleep(1)  # Sleep for 1 second

    print("Ended")
    st.session_state.timer_running = False

st.title("Countdown Timer")

if "remaining_time" not in st.session_state:
    st.session_state.remaining_time = INTERVIEW_DURATION
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.datetime.now()

timer_placeholder = st.empty()

if st.button("Start Timer"):
    # Reset the timer state
    st.session_state.remaining_time = INTERVIEW_DURATION
    st.session_state.start_time = datetime.datetime.now()
    st.session_state.timer_running = True  
    countdown_timer(timer_placeholder)

st.button(label='a')

st.session_state.interview_end = False
