import os
import sys
import json
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process, LLM
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil
# 加载环境变量


import warnings
warnings.filterwarnings(
    "ignore",
    message="Use 'content=<...>' to upload raw bytes/text content",
    category=DeprecationWarning,
    module="httpx._models"
)
# load_dotenv()
# oak = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_API_KEY"] = oak

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# 定义输出数据模型
class PrescriptionSafetyOutput(BaseModel):
    Conflict_score: int
    ConflictReason: str
    Dosage_score: int
    DosageReason: str
    Duplication_score: int
    DuplicationReason: str
    Context_score: int
    ContextReason: str
    Physical_score: int
    PhysicalReason: str
    Coverage_score: int
    CoverageReason: str
    EvaluationSummary: str

@CrewBase
class SafetyCheckerCrew():
    @agent
    def safety_checker_agent(self) -> Agent:
        """安全评估 Agent"""
        return Agent(
            config=self.agents_config['safety_checker_agent'],
            verbose=True,
            llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434")

        )

    @task
    def evaluate_prescription_safety_task(self) -> Task:
        """任务：评估处方安全性"""
        return Task(
            config=self.tasks_config['evaluate_prescription_safety_task'],
            output_pydantic=PrescriptionSafetyOutput,
            output_file="output/prescription_safety_evaluation.json",
        )

    @crew
    def crew(self) -> Crew:
        """创建安全评估 Crew"""
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


def load_prescription(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"[Error] 无法加载处方文件 {file_path}: {e}")
        return {}

def run(id):
    patient_id = str(id)
    input_prescription_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Prescription/Prescription.json")
    prescription = load_json_as_text(input_prescription_file) if os.path.exists(input_prescription_file) else ""
   
    input_diagnose_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/discharge_diagnosis.txt")
    diagnosis = open(input_diagnose_file, 'r', encoding='utf-8').read() if os.path.exists(input_diagnose_file) else ""


    input_demo_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/social_history_and_family_history.txt")
    demo_content = open(input_demo_file, 'r', encoding='utf-8').read() if os.path.exists(input_demo_file) else ""

    input_pysical_exam_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/physical_exam.txt")
    physical_exam_content = open(input_pysical_exam_file, 'r', encoding='utf-8').read() if os.path.exists(input_pysical_exam_file) else ""


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

    if not prescription:
        print("[Error] 输入处方数据为空，无法继续执行。")
        return

    # 执行 Crew
    result = SafetyCheckerCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result)

    target_folder = os.path.join(PROJECT_ROOT,f"Blackboard/Contents/{patient_id}/Safety_Check")
    os.makedirs(target_folder, exist_ok=True)

    output_file_name = "safety_check.json"
    source_file = os.path.join(PROJECT_ROOT, "output/prescription_safety_evaluation.json")
    target_path = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Safety_Check", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to {target_path}")

    safe_check_folder = os.path.join(PROJECT_ROOT, f"Blackboard/Contents/{patient_id}/Safety_Check")
    os.makedirs(safe_check_folder, exist_ok=True)

    # DDI_file = f"./Blackboard/Contents/{patient_id}/Drug_Drug_Interaction/DDI.json"
    # extract_revised_trace(DDI_file, trace_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[Error] 请提供病人编号作为参数，例如: python prescription.py 1055")
        sys.exit(1)

    id = sys.argv[1]
    run(id)