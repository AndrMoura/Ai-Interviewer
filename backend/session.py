import redis
import json

class SessionManager:
    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.client = redis.from_url(redis_url)

    def create_session(self, session_id, data):
        self.client.set(session_id, json.dumps(data))

    def get_session(self, session_id):
        session = self.client.get(session_id)
        return json.loads(session) if session else None

    def remove_session(self, session_id):
        self.client.delete(session_id)