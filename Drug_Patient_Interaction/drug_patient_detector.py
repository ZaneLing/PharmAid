import os
import shutil
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
import sys
from textwrap import dedent
from pydantic import BaseModel
from datetime import datetime
import json
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

import warnings
warnings.filterwarnings(
    "ignore",
    message="Use 'content=<...>' to upload raw bytes/text content",
    category=DeprecationWarning,
    module="httpx._models"
)

# # 加载环境变量
# load_dotenv()
# oak = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_API_KEY"] = oak


# 定义输出数据模型
class InteractionAnalysis(BaseModel):
    PhysicalExamConflict: bool
    PhysicalExamExplanation: str
    PhysicalExamRiskLevel: str
    SocialFamilyConflict: bool
    SocialFamilyExplanation: str
    SocialFamilyRiskLevel: str
    RevisedReason: str
    RevisedSuggestion: str
    RevisedPrescription: list[str]

@CrewBase
class Drug_Patient_Interaction_Crew():
    @agent
    def drug_patient_interaction_analyzer(self) -> Agent:
        """Agent 用于分析药物与患者之间的交互"""
        return Agent(
            config=self.agents_config['drug_patient_interaction_analyzer'],
            verbose=True,
            # llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434")
            llm=LLM(model="ollama/qwen3:8b", base_url="http://localhost:11434"),
            #llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434"),
            #llm=LLM(model="ollama/deepseek-r1:8b", base_url="http://localhost:11434"),


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

def extract_revised_trace(input_file, output_folder):
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 提取 RevisedSuggestion 和 RevisedPrescription
        revised_trace = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ConflictionType": "DPI",
            "RevisedReason": data.get("RevisedReason", ""),
            "RevisedSuggestion": data.get("RevisedSuggestion", ""),
            "RevisedPrescription": data.get("RevisedPrescription", [])
        }
        
        # 确定 ReviseTrace.json 的路径
        output_file = os.path.join(output_folder, "ReviseTrace.json")
        
        # 如果文件存在，加载现有数据
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as outfile:
                existing_data = json.load(outfile)
        else:
            existing_data = []
        
        # 将新的 revised_trace 添加到现有数据中
        existing_data.append(revised_trace)
        
        # 保存更新后的数据到 ReviseTrace.json
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(existing_data, outfile, ensure_ascii=False, indent=4)
        
        print(f"Revised trace has been saved to {output_file}")
    except Exception as e:
        print(f"[Error] Failed to extract revised trace: {e}")

def run_dpi(id):

    patient_id = str(id) 
    input_prescription_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Prescription/Prescription.json")
    prescription = load_json_as_text(input_prescription_file) if os.path.exists(input_prescription_file) else ""
   
    input_diagnose_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/discharge_diagnosis.txt")
    diagnosis = open(input_diagnose_file, 'r', encoding='utf-8').read() if os.path.exists(input_diagnose_file) else ""


    input_demo_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/social_history_and_family_history.txt")
    demo_content = open(input_demo_file, 'r', encoding='utf-8').read() if os.path.exists(input_demo_file) else ""

    input_pysical_exam_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/physical_exam.txt")
    physical_exam_content = open(input_pysical_exam_file, 'r', encoding='utf-8').read() if os.path.exists(input_pysical_exam_file) else ""

    # input_allergy_file = f"./Blackboard/Contents/{patient_id}/Patient_Info/Allergies.json"
    # input_physical_exam_file = f"./Blackboard/Contents/{patient_id}/Patient_Info/Physical_Exam.json"
    # input_social_file = f"./Blackboard/Contents/{patient_id}/Patient_Info/Social_history.json"
    # input_hpi_file = f"./Blackboard/Contents/{patient_id}/Patient_Info/History_of_Present_Illness.json"
    # input_family_file = f"./Blackboard/Contents/{patient_id}/Patient_Info/Family_history.json"

    # allergy_content = load_json_as_text(input_allergy_file)
    #physical_exam_content = load_json_as_text(input_physical_exam_file)
    # social_family_content = load_json_as_text(input_social_file) + load_json_as_text(input_family_file)
    # hpi_content = load_json_as_text(input_hpi_file)


    print("--------------------------")
    print(diagnosis)
    print(prescription)
    print(f"----------{patient_id}----------")
    print(physical_exam_content)
    print(demo_content)

    inputs = {
        'diagnosis': diagnosis,
        'prescription': prescription,
        'physical_exam': physical_exam_content,
        'social_family': demo_content,
    }
    # 执行 Crew
    result = Drug_Patient_Interaction_Crew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")
    
    # 创建目标文件夹
    target_folder = os.path.join(PROJECT_ROOT,f"Blackboard/Contents/{patient_id}/Drug_Patient_Interaction")
    os.makedirs(target_folder, exist_ok=True)

    output_file_name = "DPI.json"
    source_file = os.path.join(PROJECT_ROOT, "output/drug_patient_interaction.json")#'output/drug_patient_interaction.json'
    target_path = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Drug_Patient_Interaction", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to {target_path}")

    trace_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/ReviseTrace")
    os.makedirs(trace_folder, exist_ok=True)

    DPI_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Drug_Patient_Interaction/DPI.json")
    extract_revised_trace(DPI_file, trace_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[Error] 请提供病人编号作为参数，例如: python prescription.py 1055")
        sys.exit(1)

    id = sys.argv[1]
    run_dpi(id)