import os
import shutil
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from textwrap import dedent
from pydantic import BaseModel
import json
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

    input_patient_demo_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Patient_demographics.json"
    input_patient_sf_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Social_history_and_family_history.json"
    input_patient_hpi_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/History_of_present_illness.json"
    input_patient_other_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Other_relevant_information_before_the_admission.json"
    input_ins_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Inspection_findings.json"
    patient_info = load_json_as_text(input_patient_demo_file) + load_json_as_text(input_patient_other_file) + load_json_as_text(input_patient_sf_file)+ load_json_as_text(input_ins_file)+load_json_as_text(input_patient_hpi_file)
    
    input_prescription_file = f"../BlackBoard/Contents/{patient_id}/Prescription/Prescription.json"
    prescription = load_json_as_text(input_prescription_file)
    
    print("--------------------------")
    print(patient_info)
    print(prescription)
    inputs = {
        'patient_info': patient_info,
        'prescription': prescription
    }
    # 执行 Crew
    result = Drug_Patient_Interaction_Crew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")

    output_file_name = "DPI.json"
    source_file = 'output/drug_patient_interaction.json'
    target_path = os.path.join(f"../Blackboard/Contents/{patient_id}/Drug_Patient_Interaction", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to {target_path}")

if __name__ == "__main__":
    run()