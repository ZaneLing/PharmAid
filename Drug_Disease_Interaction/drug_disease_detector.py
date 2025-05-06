import os
import json
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

# 定义输出数据模型
class ConflictDetectionOutput(BaseModel):
    Conflict: bool  # 是否存在冲突
    Explanation: str  # 冲突的解释
    Alternative: list[str]  # 替代方案

@CrewBase
class DrugDiseaseDetectorCrew():
    @agent
    def drug_disease_detector_agent(self) -> Agent:
        """Agent 用于检测药物与疾病的冲突"""
        return Agent(
            config=self.agents_config['drug_disease_detector_agent'],
            verbose=True
        )

    @task
    def detect_conflict_task(self) -> Task:
        """任务：检测药物与疾病的冲突"""
        return Task(
            config=self.tasks_config['detect_conflict_task'],
            output_pydantic=ConflictDetectionOutput,
            output_file="output/drug_disease_conflict.json",
        )

    @crew
    def crew(self) -> Crew:
        """创建检测冲突的 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

def load_inputs_from_file(file_path):
    """
    从 JSON 文件中加载输入数据。
    :param file_path: JSON 文件路径
    :return: 包含病人信息和处方药物的输入字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"[Error] 无法加载输入文件 {file_path}: {e}")
        return {}
def load_json_as_text(file_path):
    """
    将 JSON 文件的内容加载为纯文本字符串。
    :param file_path: JSON 文件路径
    :return: JSON 文件内容的字符串表示
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return json.dumps(data, ensure_ascii=False, indent=4)  # 将 JSON 转换为格式化的字符串
    except Exception as e:
        print(f"[Error] 无法加载输入文件 {file_path}: {e}")
        return ""
    
def run():

    patient_id = 1058
    # 输入文件路径
    input_allege_file = f"../Blackboard/Contents/{patient_id}/Allergy_history_past_medical_history.json"
    input_cm_file = f"../Blackboard/Contents/{patient_id}/Current_medications.json"
    input_hpi_file = f"../Blackboard/Contents/{patient_id}/Current_medications.json"
    drug_disease_info = load_json_as_text(input_allege_file) + load_json_as_text(input_cm_file) + load_json_as_text(input_hpi_file)

    # input_patient_demo_file = f"../Blackboard/Contents/{patient_id}/Patient_demographics.json"
    # input_patient_sf_file = f"../Blackboard/Contents/{patient_id}/Social_history_and_family_history.json"
    # input_patient_other_file = f"../Blackboard/Contents/{patient_id}/Other_relevant_information_before_the_admission.json"
    # patient_info = load_json_as_text(input_patient_demo_file) + load_json_as_text(input_patient_other_file) + load_json_as_text(input_patient_sf_file)
    
    input_prescription_file = f"../BlackBoard/Contents/{patient_id}/Prescription/Prescription.json"
    prescription = load_json_as_text(input_prescription_file)
    
    print("--------------------------")
    print(drug_disease_info)
    print(prescription)
    inputs = {
        'drug_disease_info': drug_disease_info,
        'prescription': prescription
    }

    if not inputs:
        print("[Error] 输入数据为空，无法继续执行。")
        return

    # 执行 Crew
    result = DrugDiseaseDetectorCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    # 保存结果到 JSON 文件
    output_file = "output/drug_disease_conflict.json"
    os.makedirs("output", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result.raw, f, ensure_ascii=False, indent=4)
    print(f"\nConflict detection result saved to {output_file}")

if __name__ == "__main__":
    run()