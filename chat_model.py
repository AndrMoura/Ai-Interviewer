from langchain.chat_models import ChatOllama
from langchain.chains import LLMChain
from prompt import interviewer_prompt
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory


class InterViewer:
    def __init__(self, model_name, questions):
        self.model_name = model_name
        self.llm = ChatOllama(
            model="llama3.2:1b",
            temperature=0.5,
        )
        self.questions = questions

        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    interviewer_prompt.format(questions=questions)
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.interviewer = LLMChain(
            llm=self.llm, prompt=self.prompt, memory=self.memory, verbose=False
        )
        self.first_question = "Hello and welcome! I'm Bob, your interviewer, for this session . \
        For the next 10 minutes I will ask you questions regarding your experience for the position role Django Developer. \
        Can you can start by telling me a bit about your background experience?"

    def generate_question(self, user_response: str) -> str:
        """generate the next interviewer question"""

        next_question = self.interviewer.predict(input=user_response)
        return next_question
