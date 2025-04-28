import os
import shutil
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from textwrap import dedent
from pydantic import BaseModel
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# 示例输入数据
patient_info = {
    "Name": "John Doe",
    "Age": 45,
    "Gender": "Male",
    "MedicalHistory": ["Hypertension", "Diabetes"],
    "CurrentConditions": ["Kidney dysfunction"]
}

drug_list = {
    "ibuprofen","aspirin", "lisinopril"
}

# 定义输出数据模型
class InteractionAnalysis(BaseModel):
    ConflictionOrNot: bool
    InteractionAnalysis: dict  # 包含是否有冲突、冲突原因和替代药物
    DrugList: list[str]  # 药物列表

@CrewBase
class Drug_Patient_Interaction_Crew():
    @agent
    def drug_patient_interaction_analyzer(self) -> Agent:
        """Agent 用于分析药物与患者之间的交互"""
        return Agent(
            config=self.agents_config['drug_patient_interaction_analyzer'],
            verbose=True
        )
    
    @task
    def analyze_drug_patient_interaction_task(self) -> Task:
        """Task 用于生成药物与患者交互分析结果"""
        return Task(
            config=self.tasks_config['analyze_drug_patient_interaction_task'],
            output_pydantic=InteractionAnalysis,
            output_file="output/drug_patient_interaction.json",
        )

    @crew
    def crew(self) -> Crew:
        """创建用于分析药物与患者交互的 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

def run():
    # 输入患者信息和药物信息
    inputs = {
        'patient_info': patient_info,
        'drug_list': drug_list
    }

    # 执行 Crew
    result = Drug_Patient_Interaction_Crew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")


if __name__ == "__main__":
    run()