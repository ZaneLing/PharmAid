from crewai import Task
from textwrap import dedent
from pydantic import BaseModel

class QuestionAnswer(BaseModel):
    Question: str
    Answer: str
    Source: str

class PharmacyQATasks:
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"

    def generate_questions_task(self, agent, knowledge):
        return Task(
            description=dedent(
                f"""
            Based on the following pharmacology knowledge, generate multiple-choice questions.
            Each question should have one correct answer and provide the source of the knowledge.
            {self.__tip_section()}
            Pharmacology Knowledge:
            {knowledge}
            """
            ),
            expected_output="A list of multiple-choice questions with answers and sources",
            output_pydantic=QuestionAnswer,
            output_file="output/pharmacy_questions.json",
            agent=agent,
        )