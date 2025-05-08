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
class PrescriptionOutput(BaseModel):
    Prescription: list[dict]  # 包含药物、剂量、方式和解释的列表

@CrewBase
class PrescriptionCrew():
    @agent
    def doctor_pharmacist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['doctor_pharmacist_agent'],
            verbose=True
        )

    @task
    def generate_prescription_task(self) -> Task:
        """任务：生成药物列表、使用方案和可解释性"""
        return Task(
            config=self.tasks_config['generate_prescription_task'],
            output_pydantic=PrescriptionOutput,
            output_file="output/prescription.json",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


def load_json_as_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return json.dumps(data, ensure_ascii=False, indent=4)  # 将 JSON 转换为格式化的字符串
    except Exception as e:
        print(f"[Error] 无法加载输入文件 {file_path}: {e}")
        return ""

def run():
    patient_id = "1058"
    # 构造输入文件路径
    input_file = f"../BlackBoard/Contents/{patient_id}/Patient_Info/Chief_complaint_and_Discharge_Diagnoses.json"

    # 将 JSON 文件内容加载为文本
    input_text = load_json_as_text(input_file)
    print("---------Prescription----------")
    print(input_text)

    if not input_text:
        print("[Error] 输入数据为空，无法继续执行。")
        return
    
    inputs = {
        'statement': input_text,
    }

    # 执行 Crew
    print(f"[Prescription] 处理患者ID: {patient_id}")
    result = PrescriptionCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result)

    output_file_name = "Prescription.json"
    source_file = 'output/prescription.json'
    target_path = os.path.join(f"../Blackboard/Contents/{patient_id}/Prescription", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to {target_path}")

if __name__ == "__main__":
    run()