from langchain.schema import AIMessage, BaseMessage
from typing import List


def transform_interview(conversation_data: List[BaseMessage]):

    messages_list = []

    for msg in conversation_data:
        role = "AI" if isinstance(msg, AIMessage) else "User"
        messages_list.append({"role": role, "message": msg.content})

    return messages_list

