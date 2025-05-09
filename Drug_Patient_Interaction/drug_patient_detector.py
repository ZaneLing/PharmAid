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


# 定义输出数据模型
class InteractionAnalysis(BaseModel):
    AllergyConflict: bool
    AllergyExplanation: str
    AllergyRiskLevel: str
    PhysicalExamConflict: bool
    PhysicalExamExplanation: str
    PhysicalExamRiskLevel: str
    HPIConflict: bool
    HPIExplanation: str
    HPIRiskLevel: str
    SocialFamilyConflict: bool
    SocialFamilyExplanation: str
    SocialFamilyRiskLevel: str
    RevisedSuggestion: str
    RevisedPrescription: list[str]

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

    patient_id = "1055"    
    input_prescription_file = f"../BlackBoard/Contents/{patient_id}/Prescription/Prescription.json"
    prescription = load_json_as_text(input_prescription_file)
    
    input_diagnose_file = f"../BlackBoard/Contents/{patient_id}/Patient_Info/Discharge_Diagnose.json"
    diagnoses_content = load_json_as_text(input_diagnose_file)

    input_allergy_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Allergies.json"
    input_physical_exam_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Physical_Exam.json"
    input_social_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Social_history.json"
    input_hpi_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/History_of_Present_Illness.json"
    input_family_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Family_history.json"

    allergy_content = load_json_as_text(input_allergy_file)
    physical_exam_content = load_json_as_text(input_physical_exam_file)
    social_family_content = load_json_as_text(input_social_file) + load_json_as_text(input_family_file)
    hpi_content = load_json_as_text(input_hpi_file)


    print("--------------------------")
    print(diagnoses_content)
    print(prescription)
    print(f"----------{patient_id}----------")
    print(allergy_content)
    print(physical_exam_content)
    print(social_family_content)
    print(hpi_content)

    inputs = {
        'diagnoses': diagnoses_content,
        'prescription': prescription,
        'allergy': allergy_content,
        'physical_exam': physical_exam_content,
        'social_family': social_family_content,
        'hpi': hpi_content,
    }
    # 执行 Crew
    result = Drug_Patient_Interaction_Crew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")
    
    # 创建目标文件夹
    target_folder = os.path.join(f"../Blackboard/Contents/{patient_id}/Drug_Patient_Interaction")
    os.makedirs(target_folder, exist_ok=True)

    output_file_name = "DPI.json"
    source_file = 'output/drug_patient_interaction.json'
    target_path = os.path.join(f"../Blackboard/Contents/{patient_id}/Drug_Patient_Interaction", output_file_name)

    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to {target_path}")

if __name__ == "__main__":
    run()