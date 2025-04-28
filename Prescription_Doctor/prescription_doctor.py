from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import shutil
from textwrap import dedent
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak
import json

# input_data = "My name is Li Fang, 42 years old, teacher. In the past two months, I have sustained back pain (aggravated by sitting/standing for a long time), stomach distension and acid reflux after meals, numbness in my right hand, and weight inexplicably dropped 3 kilograms. Irregular diet (often do not eat breakfast, dinner takeout greasy), lack of exercise, stay up late to prepare classes until 22 o 'clock, poor sleep (about 1 hour to sleep), 10 years of smoking history (now changed to electronic cigarettes). The mother suffers from diabetes, and the blood lipid in the physical examination last year has not been treated."
symptom_json = {"symptom": ["Back pain (aggravated by sitting/standing for a long time)", "Stomach distension and acid reflux after meals", "Numbness in right hand", "Inexplicable weight loss of 3 kilograms"]}

input_data = symptom_json

# 定义 Prescription2Symptom 数据模型
class PrescriptionSymptomPair(BaseModel):
    symptom: str  # 症状描述
    medicine_name: str
    prescription: str  # 对应的处方描述

class Prescription2Symptom(BaseModel):
    Prescription_Symptom_Pair: list[PrescriptionSymptomPair]  

@CrewBase
class Patient_Prescription_Crew():
    @agent
    def prescription_doctor(self) -> Agent:
        return Agent(
            config = self.agents_config['prescription_doctor'],
            verbose = True
        )

    @task
    def recommend_prescription_task(self) -> Task:
        return Task(
            config = self.tasks_config['recommend_prescription_task'],
            output_pydantic = Prescription2Symptom,
            output_file = "output/patient_prescription.json",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
    
def run():
        inputs = {
            'symptom': input_data
        }

        result = Patient_Prescription_Crew().crew().kickoff(inputs=inputs)
        
        print("\n\n=== FINAL REPORT ===\n\n")
        print(result.raw)

        print("Over.")

if __name__ == "__main__":
    run()