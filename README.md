# AI Interviewer

Welcome to the AI Interviewer! This is a propotype web application that allows you to interview candidates to a specific job role using a voice interface. You can also use it to practice for interviews.

## **Key Features**

- **Customizable Job Roles:**  
  Define job roles with detailed descriptions to align with your yours or organization's needs.

- **Tailored Interview Questions:**  
  Add and organize specific interview questions for each job role to test relevant skills and qualifications.

- **Transcriptions:**  
  All interviews are transcribed, providing candidates with a complete transcript for review and improvement with automatic evaluation.



# Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/ai-interviewer.git
```
## Python
2. Install venv and the dependencies:
```
python -m venv venv
pip install -r backend/requirements.txt
```
3. Install ffmpeg:
```
sudo apt update && sudo apt install ffmpeg
```

## Frontend

1. Install nvm:
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
nvm install 18
nvm use 18
nvm alias default 18
```
If nvm not found, try:
```
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

# Running the app

Run the script to fill the database with two users (admin and normal user) and one job role:
```bash
python -m backend.init_db
```

Export your OpenAI API key:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```
Finally, run the app:

```
uvicorn backend.main:app
npm start
```
To quickly test the app, login as admin (username: adminuser, password: adminpassword) and start a new interview. 🚀
By default, the app uses the `gpt-4o-mini`. Check the `backend/constants.py` file to change the model.
