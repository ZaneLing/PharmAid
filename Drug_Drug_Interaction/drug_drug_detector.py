import os
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
import json
import shutil

import warnings
warnings.filterwarnings(
    "ignore",
    message="Use 'content=<...>' to upload raw bytes/text content",
    category=DeprecationWarning,
    module="httpx._models"
)


from textwrap import dedent
from pydantic import BaseModel

from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# load_dotenv()
# oak = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_API_KEY"] = oak

from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

from crewai_tools import CSVSearchTool, JSONSearchTool
from datetime import datetime
import sys
# import pandas as pd

# # 读取 CSV 文件，指定编码为 'ISO-8859-1'，并跳过无法解码的字符
# df = pd.read_csv('drugbank_clean.csv', encoding='ISO-8859-1', encoding_errors='ignore')

# # 将 DataFrame 保存为 JSON 文件
# df.to_json('drugbank_clean.json', orient='records')

#drug_csv_searcher = CSVSearchTool('drugbank_clean_utf8.csv')
#drug_json_searcher = JSONSearchTool('drugbank_clean.json')
input_data = "Lepirudin" 

class DrugConflictDetector(BaseModel):
    MOAAnalysisStep: list[str]
    PMHAnalysisStep: list[str]
    MoaConflict: bool  # 是否存在冲突
    MoaExplanation: str  # 冲突的解释
    MoaRiskLevel: str  # 风险等级
    PmhConfliect: bool  # 是否存在冲突
    PmhExplanation: str  # 冲突的解释
    PmhRiskLevel: str  # 风险等级
    RevisedReason: str  # 替代原因
    RevisedSuggestion: str  # 替代方案
    RevisedPrescription: list[str]  # 替代方案

@CrewBase
class Drug_Conflict_Detector_Crew():
    @agent
    def drug_conflict_detector(self) -> Agent:
        return Agent(
            config = self.agents_config['drug_conflict_detector'],
            #tools = [drug_json_searcher],
            verbose = True,
            llm=LLM(model="ollama/qwen3:8b", base_url="http://localhost:11434"),
            #llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434"),
            #llm=LLM(model="ollama/deepseek-r1:8b", base_url="http://localhost:11434"),
            # llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434")

        )
    
    @task
    def drug_conflict_detector_task(self) -> Task:
        return Task(
            config = self.tasks_config['drug_conflict_detector_task'],
            output_pydantic = DrugConflictDetector,
            output_file = "output/drug_drug_interaction.json",
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
            "ConflictionType": "DDI",
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

def run_ddi(id):
        patient_id = str(id)
        
        input_diagnose_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/discharge_diagnosis.txt")
        input_moa_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/medications_on_admission.txt")
        input_pmh_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/past_medical_history.txt")


        diagnosis = open(input_diagnose_file, 'r', encoding='utf-8').read() if os.path.exists(input_diagnose_file) else ""
        medications_on_admission = open(input_moa_file, 'r', encoding='utf-8').read() if os.path.exists(input_moa_file) else ""
        past_medical_history = open(input_pmh_file, 'r', encoding='utf-8').read() if os.path.exists(input_pmh_file) else ""


        #input_moa_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Patient_Info/Medications_on_Admissions.json")
        #input_pmh_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Patient_Info/Past_Medical_History.json")

        input_prescription_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Prescription/Prescription.json")
        prescription = load_json_as_text(input_prescription_file) if os.path.exists(input_prescription_file) else ""
        # input_diagnosis_file = f"./BlackBoard/Contents/{patient_id}/Patient_Info/Discharge_Diagnose.json"
        #diagnoses = load_json_as_text(input_diagnosis_file)

        print(f"-----------{patient_id}---------------")
        print(diagnosis)
        print(prescription)
        print(f"-----------{patient_id}---------------")
        print(medications_on_admission)
        print("-----------pmh---------------")
        print(past_medical_history)

        inputs = {
            'moa': medications_on_admission,
            'pmh': past_medical_history,
            'diagnose': diagnosis,
            'prescription': prescription,
        }

        result = Drug_Conflict_Detector_Crew().crew().kickoff(inputs=inputs)

        print("\n\n=== FINAL REPORT ===\n\n")
        print(result.raw)

        print("Over.")

        # 创建目标文件夹
        target_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Drug_Drug_Interaction")
        os.makedirs(target_folder, exist_ok=True)

        output_file_name = "DDI.json"
        source_file = os.path.join(PROJECT_ROOT, "output/drug_drug_interaction.json")#'output/drug_drug_interaction.json'
        target_path = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Drug_Drug_Interaction", output_file_name)

        shutil.copy2(source_file, target_path)
        print(f"\n\nReport has been saved to {target_path}")

        trace_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/ReviseTrace")
        os.makedirs(trace_folder, exist_ok=True)

        DDI_file = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Drug_Drug_Interaction/DDI.json") # f"./Blackboard/Contents/{patient_id}/Drug_Drug_Interaction/DDI.json"
        extract_revised_trace(DDI_file, trace_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[Error] 请提供病人编号作为参数，例如: python prescription.py 1055")
        sys.exit(1)

    id = sys.argv[1]
    run_ddi(id)
 



