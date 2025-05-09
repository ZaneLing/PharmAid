import os
import json
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from textwrap import dedent
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil

# 加载环境变量
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# 定义输出数据模型
class PrescriptionSafetyOutput(BaseModel):
    FinalPrescription: list[dict]  # 包含药物、剂量、方式和解释的列表
    SafetyCheck: dict  # 安全检查结果，包括冲突和建议
    Suggestion: str

@CrewBase
class PrescriptionSafetyCheckerCrew():
    @agent
    def safety_checker_agent(self) -> Agent:
        """安全检查 Agent"""
        return Agent(
            config=self.agents_config['safety_checker_agent'],
            verbose=True
        )

    @task
    def perform_safety_check_task(self) -> Task:
        """任务：执行处方安全检查"""
        return Task(
            config=self.tasks_config['perform_safety_check_task'],
            output_pydantic=PrescriptionSafetyOutput,
            output_file="output/final_prescription.json",
        )

    @crew
    def crew(self) -> Crew:
        """创建安全检查 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

def load_prescription(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get("Prescription", [])
    except Exception as e:
        print(f"[Error] 无法加载处方文件 {file_path}: {e}")
        return []

def run():
    # 输入处方文件路径
    patient_id = "1058"

    input_prescription_file = f"../BlackBoard/Contents/{patient_id}/Prescription/Prescription.json"

    # 加载处方数据
    prescription = load_prescription(input_prescription_file)

    if not prescription:
        print("[Error] 输入处方数据为空，无法继续执行。")
        return

    # 构造输入
    inputs = {
        'prescription': prescription
    }

    # 执行 Crew
    result = PrescriptionSafetyCheckerCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result)

    output_file_name = "Result.json"
    source_file = 'output/final_prescription.json'
    target_path = os.path.join(f"../Blackboard/Contents/{patient_id}/Result", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to {target_path}")

if __name__ == "__main__":
    run()