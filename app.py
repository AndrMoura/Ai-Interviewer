import yaml
import datetime
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from helper import generate_questions

with open("./credentials.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

DEBUG = True

ROLE_CFG = {
    "Data Science": "The Data Scientist will analyze large datasets to provide insights and support data-driven decision-making. This role requires proficiency in machine learning, data mining, and statistical analysis. The candidate should demonstrate strong programming skills in Python, experience with SQL, and the ability to communicate findings clearly. Responsibilities include building predictive models, optimizing data pipelines, and collaborating with cross-functional teams."
}

INTERVIEW_DURATION = 1 * 60


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
    authenticator.login("main")

    if st.session_state.get("authentication_status"):
        login_sc = st.info("You are logged in", icon="ℹ️")
        name = st.session_state["name"]
        username = st.session_state["username"]

        if "viewer" in st.session_state["roles"]:
            st.title("AI InterViewer 💬")

            with st.expander("Admin Settings"):
                must_have_questions = st.text_area(
                    "Custom Question Suggestions (one per line)",
                    key="custom_questions",
                    help="Add custom questions for the interview",
                )

            # Input section
            upload_type = st.radio("Choose input type:", ["Text", "PDF"])

            if upload_type == "Text":
                resume_text = st.text_area(
                    "Enter your resume or background information:"
                )
            else:
                uploaded_file = st.file_uploader(
                    "Upload your CV (PDF)", type=["pdf"], accept_multiple_files=False
                )
                if uploaded_file:
                    st.info("PDF functionality will be implemented later")
                    resume_text = ""

            role_option = st.selectbox(
                "What Role do you want to apply to:",
                (
                    "Data Science",
                    "Software Eng",
                ),
            )
            role_description = ROLE_CFG[role_option]
            if st.button("Start Interview"):
                if upload_type == "Text" and resume_text:
                    with st.spinner("Preparing your interview..."):
                        must_questions = "\n".join(
                            [
                                "- " + question
                                for question in must_have_questions.split("\n")
                            ]
                        )
                        questions = generate_questions(
                            resume=resume_text,
                            role=role_option,
                            role_description=role_description,
                            must_have_questions=must_questions,
                            model_name="llama3.2:3b",
                        )
                    reset_state()
                    st.session_state["interview_started"] = True
                    st.session_state["questions"] = questions

                    # Redirect to interview page
                    st.switch_page("pages/interview_test.py")
                else:
                    st.error("Please provide resume text before starting the interview")


if __name__ == "__main__":
    main()
