from langchain_openai import ChatOpenAI
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


class InterViewer:
    def __init__(self, model_name, questions, name, role, resume, role_description):
        self.name = name
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.5,
        )
        self.questions = questions
        self.role = role
        self.resume = resume
        self.role_description = role_description

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

    def generate_question(self, user_response: str = "ask me a question") -> str:
        """generate the next interviewer question"""

        next_question = self.interviewer.predict(input=user_response)
        return next_question


def generate_questions(
    resume, role, role_description, must_have_questions, model_name="gpt-4o-mini"
) -> str:

    question_generator_template = PromptTemplate(
        template=question_generator_prompt,
        input_variables=["role", "description", "must_have_questions" "resume_text"],
    )

    llm = ChatOpenAI(model=model_name)

    question_generator_chain = LLMChain(llm=llm, prompt=question_generator_template)

    guidelines = question_generator_chain.run(
        role=role,
        description=role_description,
        must_have_questions=must_have_questions,
        resume_text=resume,
    )

    return guidelines


def evaluate_interview(
    interview,
    role,
    role_description,
    model_name="gpt-4o-mini",
) -> str:

    evaluator_template = PromptTemplate(
        template=evaluator_prompt,
        input_variables=["role", "role_description", "interview"],
    )

    llm = ChatOpenAI(model=model_name)

    question_generator_chain = LLMChain(llm=llm, prompt=evaluator_template)

    evaluation = question_generator_chain.run(
        role=role, role_description=role_description, interview=interview
    )

    return evaluation
