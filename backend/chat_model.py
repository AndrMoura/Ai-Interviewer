import os
from langchain_community.chat_models.openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from .prompt import interviewer_prompt, question_generator_prompt, evaluator_prompt
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory
from .constants import OPENAI_MODEL_NAME, GEMINI_MODEL_NAME


def get_chat_model():
    """Factory function to return appropriate chat model based on available API keys"""
    if os.getenv("GOOGLE_API_KEY"):
        return ChatGoogleGenerativeAI(
            model=GEMINI_MODEL_NAME,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(
            model=OPENAI_MODEL_NAME,
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    else:
        raise Exception("No API keys found for chat model")
    
chat_model = get_chat_model()

class InterViewer:
    def __init__(
        self,
        guidelines,
        name,
        role,
        resume,
        role_description,
        must_have_questions,
    ):
        self.name = name
        self.llm = get_chat_model()
        self.guidelines = guidelines
        self.role = role
        self.resume = resume
        self.role_description = role_description
        self.must_have_questions = must_have_questions

        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    interviewer_prompt.format(
                        role=role,
                        role_description=role_description,
                        guidelines=guidelines,
                        must_have_questions=must_have_questions,
                    )
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.interviewer = LLMChain(
            llm=self.llm, prompt=self.prompt, memory=self.memory, verbose=False
        )
    
    def to_dict(self):
        """Serialize the InterViewer instance to a dict"""
        return {
            "guidelines": self.guidelines,
            "name": self.name,
            "role": self.role,
            "resume": self.resume,
            "role_description": self.role_description,
            "must_have_questions": self.must_have_questions,
            "first_msg": self.memory.chat_memory.messages[0].content,
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            guidelines=data.get("guidelines"),
            name=data.get("name"),
            role=data.get("role"),
            resume=data.get("resume"),
            role_description=data.get("role_description"),
            must_have_questions=data.get("must_have_questions"),
        )
        chat_memory = data.get("first_msg")
        if chat_memory:
            instance.memory.chat_memory.add_ai_message(chat_memory)
        return instance

    async def generate_question(self, user_response: str = "ask me a question") -> str:
        """generate the next interviewer question"""

        next_question = await self.interviewer.apredict(input=user_response)
        return next_question


async def generate_questions(resume, role, role_description) -> str:

    question_generator_template = PromptTemplate(
        template=question_generator_prompt,
        input_variables=["role", "role_description", "resume_text"],
    )
    llm = get_chat_model()
    question_generator_chain = LLMChain(llm=llm, prompt=question_generator_template)

    guidelines = await question_generator_chain.arun(
        role=role,
        role_description=role_description,
        resume_text=resume,
    )

    return guidelines


async def evaluate_interview(
    interview,
    role,
    role_description,
) -> str:

    evaluator_template = PromptTemplate(
        template=evaluator_prompt,
        input_variables=["role", "role_description", "interview"],
    )

    llm = get_chat_model()

    question_generator_chain = LLMChain(llm=llm, prompt=evaluator_template)

    evaluation = await question_generator_chain.arun(
        role=role, role_description=role_description, interview=interview
    )

    return evaluation
