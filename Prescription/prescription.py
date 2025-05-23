import os
import json
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
from textwrap import dedent
import sys


from pydantic import BaseModel
from dotenv import load_dotenv
import shutil
from datetime import datetime
#retro_json_path = os.path.join(PROJECT_ROOT, "BlackBoard/Contents/Retro.json")# Guidances from iteration
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


json_source = JSONKnowledgeSource(
    file_paths=["Retro.json"]
)

import warnings
warnings.filterwarnings(
    "ignore",
    message="Use 'content=<...>' to upload raw bytes/text content",
    category=DeprecationWarning,
    module="httpx._models"
)
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
            #knowledge_sources=[json_source],
            verbose=True
            # llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434")
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

def extract_revised_trace(input_file, output_folder):
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 提取 RevisedSuggestion 和 RevisedPrescription
        revised_trace = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Prescription": data.get("Prescription", ""),
        }
        
        # 确定 ReviseTrace.json 的路径
        output_file = os.path.join(output_folder, "ReviseTrace.json")
        
        # 如果文件存在，加载现有数据
# 确保目标文件夹存在
        os.makedirs(output_folder, exist_ok=True)

        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as outfile:
                existing_data = json.load(outfile)
        else:
            # 如果文件不存在，创建一个空的 JSON 文件
            existing_data = []
            with open(output_file, 'w', encoding='utf-8') as outfile:
                json.dump(existing_data, outfile, ensure_ascii=False, indent=4)
        
        # 将新的 revised_trace 添加到现有数据中
        existing_data.append(revised_trace)
        
        # 保存更新后的数据到 ReviseTrace.json
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(existing_data, outfile, ensure_ascii=False, indent=4)
        
        print(f"Revised trace has been appended to {output_file}")
    except Exception as e:
        print(f"[Error] Failed to extract revised trace: {e}")

def load_json_as_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return json.dumps(data, ensure_ascii=False, indent=4)  # 将 JSON 转换为格式化的字符串
    except Exception as e:
        print(f"[Error] 无法加载输入文件 {file_path}: {e}")
        return ""

def run_prescription(id):
    patient_id = str(id)

    #pre-processing
    input_diagnose_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/discharge_diagnosis.txt")
    diagnosis = open(input_diagnose_file, 'r', encoding='utf-8').read() if os.path.exists(input_diagnose_file) else ""
    previous_prescription_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Prescription/Prescription.json")
    DDI_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Drug_Drug_Interaction/DDI.json")
    DPI_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Drug_Patient_Interaction/DPI.json")   
    previous_prescription = load_json_as_text(previous_prescription_file) if os.path.exists(previous_prescription_file) else ""
    DDI = load_json_as_text(DDI_file) if os.path.exists(DDI_file) else ""
    DPI = load_json_as_text(DPI_file) if os.path.exists(DPI_file) else ""
    
    print(f"--------{patient_id}---------")
    print("diagnosis: ",diagnosis)

    print("----------Previous Prescription----------")
    print(previous_prescription)
    print(DDI)
    print(DPI)

    inputs = {
        'diagnosis': diagnosis,
        'previous_prescription': previous_prescription,
        'DDI': DDI,
        'DPI': DPI,
    }

    #crew
    print(f"[Prescription] patient processing...: {patient_id}")
    result = PrescriptionCrew().crew().kickoff(inputs=inputs)

    print("\n-------FINAL REPORT------\n")
    print(result)

    #post-processing
    target_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription")
    os.makedirs(target_folder, exist_ok=True)

    output_file_name = "Prescription.json"
    source_file = os.path.join(PROJECT_ROOT, "output/prescription.json")
    target_path = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Prescription", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n---------Report has been saved to {target_path}-------\n")    

    trace_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/ReviseTrace")
    os.makedirs(target_folder, exist_ok=True)

    prescription_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Prescription/Prescription.json")
    extract_revised_trace(prescription_file, trace_folder)
    print(f"\n---------Revise Trace has been saved to {trace_folder}-------\n") 

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[Error] 请提供病人编号作为参数，例如: python prescription.py 1055")
        sys.exit(1)

    id = sys.argv[1]
    run_prescription(id)