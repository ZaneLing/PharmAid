import os
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

import shutil

from textwrap import dedent
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

from crewai_tools import CSVSearchTool, JSONSearchTool

drug_json = {"Prescription_Symptom_Pair":[{"symptom":"Back pain (aggravated by sitting/standing for a long time)","medicine_name":"Ibuprofen","prescription":"Ibuprofen 400mg: Take 1 tablet every 8 hours as needed for pain relief. Do not exceed 3 tablets in 24 hours. Avoid prolonged use without medical advice."},{"symptom":"Stomach distension and acid reflux after meals","medicine_name":"Omeprazole","prescription":"Omeprazole 20mg: Take 1 capsule daily before the first meal of the day for 2 weeks. If symptoms persist, consult a healthcare professional."},{"symptom":"Numbness in right hand","medicine_name":"Methylcobalamin (Vitamin B12)","prescription":"Methylcobalamin 1500mcg: Take 1 tablet daily after a meal for 4 weeks. Follow up with a doctor if there is no improvement."},{"symptom":"Inexplicable weight loss of 3 kilograms","medicine_name":"No medication needed","prescription":"No specific medication required. It is recommended to undergo further evaluation by a healthcare provider to determine the underlying cause of weight loss."}]}

drug_data = drug_json  # 示例药物名称

patient_json = {"Name":"Li Fang","Age":"42 years old","Gender":"Female","Height_cm":"Not provided","Weight_kg":"Not provided","BadHabits":"Irregular diet (often do not eat breakfast, dinner takeout greasy), lack of exercise, stay up late until 22 o'clock, poor sleep, 10 years of smoking history (now changed to electronic cigarettes)"}

patient_info = patient_json

# 定义输出数据模型
class MedicationSchedule(BaseModel):
    DrugName: str
    Dosage: str
    Timing: str
    SpecialInstructions: str

@CrewBase
class Medication_Schedule_Crew():
    @agent
    def medication_schedule_recommender(self) -> Agent:
        """定义用于生成用药计划的 Agent"""
        return Agent(
            config=self.agents_config['medication_schedule_recommender'],
            verbose=True
        )
    
    @task
    def medication_schedule_task(self) -> Task:
        """定义生成用药计划的任务"""
        return Task(
            config=self.tasks_config['medication_schedule_task'],
            output_pydantic=MedicationSchedule,
            output_file="output/medication_schedule.json",
        )

    @crew
    def crew(self) -> Crew:
        """创建用于生成用药计划的 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

def run():
    inputs = {
        'drug': drug_data,
        'Base_Info': patient_info,
    }

    # 执行 Crew
    result = Medication_Schedule_Crew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")

    # 保存结果到指定文件夹
    drug_name = result.pydantic.DrugName
    print('Drug Name:', drug_name)
    if drug_name:
        file_name = f"{drug_name}_medication_schedule.json"
    else:
        file_name = "medication_schedule.json"
    
    source_file = 'output/medication_schedule.json'
    target_path = os.path.join('medication_schedules', file_name)
    os.makedirs('medication_schedules', exist_ok=True)
    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to medication_schedules/{file_name}")


if __name__ == "__main__":
    run()