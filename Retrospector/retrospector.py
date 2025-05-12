import os
import json
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel
import sys
from dotenv import load_dotenv
import shutil
from datetime import datetime
# 加载环境变量
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# 定义输出数据模型
class PrescriptionGuidanceOutput(BaseModel):
    Differences: list[dict]  # 标准处方和最终处方的差异
    Reflections: str  # 对差异的反思
    Guidance: list[str]  # 改进未来处方的建议

@CrewBase
class RetrospectorCrew():
    @agent
    def retrospector_agent(self) -> Agent:
        """分析和反思 Agent"""
        return Agent(
            config=self.agents_config['retrospector_agent'],
            verbose=True
        )

    @task
    def compare_prescriptions_task(self) -> Task:
        """任务：对比处方并生成指导"""
        return Task(
            config=self.tasks_config['compare_prescriptions_task'],
            output_pydantic=PrescriptionGuidanceOutput,
            output_file="output/prescription_guidance.json",
        )

    @crew
    def crew(self) -> Crew:
        """创建分析和反思的 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

def load_prescription(file_path):
    """
    从 JSON 文件中加载处方数据。
    :param file_path: JSON 文件路径
    :return: 处方数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"[Error] 无法加载处方文件 {file_path}: {e}")
        return {}

def extract_retro(input_file, output_folder):
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 提取 RevisedSuggestion 和 RevisedPrescription
        revised_trace = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Retro": data.get("Guidance", [])
        }
        
        # 确定 ReviseTrace.json 的路径
        output_file = os.path.join(output_folder, "Retro.json")
        
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
        
        print(f"Retro has been saved to {output_file}")
    except Exception as e:
        print(f"[Error] Failed to extract guidance: {e}")   

def run(id):
    patient_id = str(id)
    # 输入文件路径
    standard_prescription_file = f"./BlackBoard/Contents/{patient_id}/Patient_Info/Discharge_Medications.json"
    final_prescription_file = f"./BlackBoard/Contents/{patient_id}/Prescription/Prescription.json"
    diagnosis_file = f"./BlackBoard/Contents/{patient_id}/Patient_Info/Discharge_Diagnose.json"
    # 加载标准处方和最终处方
    standard_prescription = load_prescription(standard_prescription_file)
    final_prescription = load_prescription(final_prescription_file)
    diagnosis_contents = load_prescription(diagnosis_file)

    if not standard_prescription:
        print("[Error] 标准处方数据为空，无法继续执行。")
        return

    if not final_prescription:
        print("[Error] 最终处方数据为空，无法继续执行。")
        return

    # 构造输入
    inputs = {
        'diagnosis': diagnosis_contents,
        'standard_prescription': standard_prescription,
        'final_prescription': final_prescription
    }

    # 执行 Crew
    result = RetrospectorCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result)

    # # 创建目标文件夹
    target_folder = os.path.join(f"./BlackBoard/Contents/{patient_id}/Retro")
    os.makedirs(target_folder, exist_ok=True)

    output_file_name = "Retro.json"
    source_file = 'output/prescription_guidance.json'
    target_path = os.path.join(f"./BlackBoard/Contents/{patient_id}/Retro", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\nReport has been saved to {target_path}")

    retro_folder = os.path.join(f"./knowledge")
    os.makedirs(retro_folder, exist_ok=True)
    
    retro_file = f"./knowledge/Retro.json"
    extract_retro(retro_file, retro_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[Error] 请提供病人编号作为参数，例如: python retrospector.py 1055")
        sys.exit(1)

    id = sys.argv[1]
    run(id)