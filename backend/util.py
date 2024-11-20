
from PyPDF2 import PdfReader
from io import BytesIO
from langchain.schema import AIMessage, BaseMessage
from typing import List


def transform_interview(conversation_data: List[BaseMessage]):

    messages_list = []

    for msg in conversation_data:
        role = "AI" if isinstance(msg, AIMessage) else "User"
        messages_list.append({"role": role, "message": msg.content})

    return messages_list

def resume_reader(resume_bytes):
    resume_stream = BytesIO(resume_bytes)
    pdf_reader = PdfReader(resume_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text
