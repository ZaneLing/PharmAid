import os
import json
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel
from dotenv import load_dotenv
import shutil
# 加载环境变量
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

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
            verbose=True
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

def load_prescription(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"[Error] 无法加载处方文件 {file_path}: {e}")
        return {}

def run(id):
    patient_id = str(id)
    # 输入文件路径
    prescription_file = f"./BlackBoard/Contents/{patient_id}/Prescription/prescription.json"
    diagnosis_file = f"./BlackBoard/Contents/{patient_id}/Patient_Info/Discharge_Diagnose.json"
    patient_info_file = f"./BlackBoard/Contents/{patient_id}/Patient_Info/Allergies.json"
    physical_exam_file = f"./BlackBoard/Contents/{patient_id}/Patient_Info/Physical_Exam.json"

    # 加载处方数据
    prescription = load_prescription(prescription_file)
    diagnosis = load_prescription(diagnosis_file)
    patient_info = load_prescription(patient_info_file)
    physical_exam = load_prescription(physical_exam_file)

    if not prescription:
        print("[Error] 输入处方数据为空，无法继续执行。")
        return

    # 构造输入
    inputs = {
        'prescription': prescription,
        'diagnosis': diagnosis,
        'patient_info': patient_info,
        'physical_exam': physical_exam
    }

    # 执行 Crew
    result = SafetyCheckerCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result)

    target_folder = os.path.join(f"./Blackboard/Contents/{patient_id}/Safety_Check")
    os.makedirs(target_folder, exist_ok=True)

    output_file_name = "safety_check.json"
    source_file = 'output/prescription_safety_evaluation.json'
    target_path = os.path.join(f"./Blackboard/Contents/{patient_id}/Safety_Check", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to {target_path}")

    safe_check_folder = os.path.join(f"./Blackboard/Contents/{patient_id}/Safety_Check")
    os.makedirs(safe_check_folder, exist_ok=True)

    # DDI_file = f"./Blackboard/Contents/{patient_id}/Drug_Drug_Interaction/DDI.json"
    # extract_revised_trace(DDI_file, trace_folder)

if __name__ == "__main__":
    patient_id = 1057
    run(patient_id)