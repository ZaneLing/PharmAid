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

input_data = "My name is Li Fang, 42 years old, teacher. In the past two months, I have sustained back pain (aggravated by sitting/standing for a long time), stomach distension and acid reflux after meals, numbness in my right hand, and weight inexplicably dropped 3 kilograms. Irregular diet (often do not eat breakfast, dinner takeout greasy), lack of exercise, stay up late to prepare classes until 22 o 'clock, poor sleep (about 1 hour to sleep), 10 years of smoking history (now changed to electronic cigarettes). The mother suffers from diabetes, and the blood lipid in the physical examination last year has not been treated."

# class PatientInformation(BaseModel):
#     Name: str
#     Age: str
#     Gender: str
#     Height_cm: str
#     Weight_kg: str
#     BadHabits: str
#     Symptom: str
#     Other_informations: str

class PatientInformation(BaseModel):
    base_info: list[str]  # 基本信息，例如姓名、年龄、性别等
    special_info: list[str]  # 特殊信息，例如不良习惯、其他信息等
    symptom: list[str] 
    other_info: list[str]

@CrewBase
class Patient_Info_Crew():
    @agent
    def patient_info_cleaner(self) -> Agent:
        return Agent(
            config = self.agents_config['patient_info_cleaner'],
            verbose = True
        )

    @task
    def patient_info_cleaner_task(self) -> Task:
        return Task(
            config = self.tasks_config['patient_info_cleaner_task'],
            output_pydantic = PatientInformation,
            output_file = "output/patient_info.json",
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
            'statement': input_data
        }

        result = Patient_Info_Crew().crew().kickoff(inputs=inputs)
        
        print("\n\n=== FINAL REPORT ===\n\n")
        print(result.raw)

        print("Over.")

        # patient_name = result.pydantic.Name
        # print('Patient Name:',patient_name)
        # if patient_name:
        #     file_name = f"{patient_name}_patient_info.json"
        # else:
        #     file_name = "patient_info.json"
        

        source_file = 'output/patient_info.json'
        # target_path = os.path.join('patient_info',file_name)
        # shutil.copy2(source_file, target_path)

        # print(f"\n\nReport has been saved to patient_info/{patient_name}_patient_info.json")

if __name__ == "__main__":
    run()