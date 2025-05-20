import os
from pydantic import BaseModel
from crewai.project import CrewBase, agent, task, crew
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
# # 加载环境变量
import sys
# load_dotenv()
# oak = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_API_KEY"] = oak

# os.environ["OPEN_API_KEY"] = "sk-proj-111"

# ollama_llm=OllamaLLM(
#     model="deepseek-r1:7b", 
#     base_url="http://localhost:11434"
# )

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 定义输出数据模型
class PrescriptionOutput(BaseModel):
    DrugName: list[str]  # 药物名称列表

@CrewBase
class SingleAgentCrew():
    @agent
    def prescription_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['prescription_agent'],
            verbose=True,
            llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434")
        )

    @task
    def generate_prescription_task(self) -> Task:
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
            # model="ollama/deepseek-r1:b",
        )

def run(id):
    patient_id = str(id)

    print(PROJECT_ROOT)

    input_diagnose_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/discharge_diagnosis.txt")
    # input_diagnose_file = os.path.join(PROJECT_ROOT, f"BlackBoard/Contents/{patient_id}/Patient_Info/Discharge_Diagnose.json")
    input_demo_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/social_history_and_family_history.txt")
    input_moa_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/medications_on_admission.txt")
    input_pmh_file = os.path.join(PROJECT_ROOT, f"CCMDataset/CCMD/{patient_id}/past_medical_history.txt")

    diagnosis = open(input_diagnose_file, 'r', encoding='utf-8').read()
    demo_info = open(input_demo_file, 'r', encoding='utf-8').read()
    medications_on_admission = open(input_moa_file, 'r', encoding='utf-8').read()
    past_medical_history = open(input_pmh_file, 'r', encoding='utf-8').read()

    patient_info = demo_info + medications_on_admission + past_medical_history  

    # 构造输入
    inputs = {
        'diagnose': diagnosis,
        'patient_info': patient_info
    }

    # 执行 Crew
    result = SingleAgentCrew().crew().kickoff(inputs=inputs)

    # 打印输出
    print("\n\n=== GENERATED PRESCRIPTION ===\n\n")
    print(result.raw)

    # 创建目标文件夹路径
    evaluation_folder = os.path.join(PROJECT_ROOT, f"ComparativeTest/Single_Agent/evaluation/{patient_id}")
    os.makedirs(evaluation_folder, exist_ok=True)

    # 定义目标文件路径
    target_file = os.path.join(evaluation_folder, "output_prescription.json")

    # 复制文件
    source_file = os.path.join(PROJECT_ROOT, "ComparativeTest/Single_Agent/output/prescription.json")
    if os.path.exists(source_file):
        with open(source_file, 'r', encoding='utf-8') as src, open(target_file, 'w', encoding='utf-8') as dest:
            dest.write(src.read())
        print(f"Prescription output copied to: {target_file}")
    else:
        print(f"Source file not found: {source_file}")

if __name__ == "__main__":
    # 示例患者信息

    if len(sys.argv) != 2:
        print("[Error] 请提供参数")
        sys.exit(1)

    patient_id = sys.argv[1]

    run(patient_id)

