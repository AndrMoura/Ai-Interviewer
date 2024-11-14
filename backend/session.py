from typing import Dict
from .chat_model import InterViewer

class SessionManager:
    """Manages interview sessions"""
    def __init__(self):
        self.sessions: Dict[str, InterViewer] = {}

    def create_session(self, session_id: str, model: InterViewer):
        # Initialize a unique InterViewer instance per session
        self.sessions[session_id] = model

    def get_session(self, session_id: str) -> InterViewer:
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
