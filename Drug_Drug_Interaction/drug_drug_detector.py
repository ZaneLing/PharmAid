import os
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import json
import shutil

from textwrap import dedent
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)

from crewai_tools import CSVSearchTool, JSONSearchTool
# import pandas as pd

# # 读取 CSV 文件，指定编码为 'ISO-8859-1'，并跳过无法解码的字符
# df = pd.read_csv('drugbank_clean.csv', encoding='ISO-8859-1', encoding_errors='ignore')

# # 将 DataFrame 保存为 JSON 文件
# df.to_json('drugbank_clean.json', orient='records')

#drug_csv_searcher = CSVSearchTool('drugbank_clean_utf8.csv')
#drug_json_searcher = JSONSearchTool('drugbank_clean.json')
input_data = "Lepirudin" 

class DrugConflictDetector(BaseModel):
    # DrugName: str
    # Drug_Explanation: str
    # Drug_Interactions_List: list[str]
    # Other_Information: str
    Conflict: bool  # 是否存在冲突
    Explanation: str  # 冲突的解释
    Alternative: list[str]  # 替代方案

@CrewBase
class Drug_Conflict_Detector_Crew():
    @agent
    def drug_conflict_detector(self) -> Agent:
        return Agent(
            config = self.agents_config['drug_conflict_detector'],
            #tools = [drug_json_searcher],
            verbose = True
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
    
def run():
        patient_id = "1058"

        input_ahhm_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Allergy_history_past_medical_history.json"
        input_cm_file = f"../Blackboard/Contents/{patient_id}/Patient_Info/Current_medications.json"
        general_info = load_json_as_text(input_ahhm_file) + load_json_as_text(input_cm_file)
        
        input_prescription_file = f"../BlackBoard/Contents/{patient_id}/Prescription/Prescription.json"
        prescription = load_json_as_text(input_prescription_file)
        
        print("--------------------------")
        print(general_info)
        print(prescription)
        inputs = {
            'prescription': prescription,
            'general_info':general_info
        }

        result = Drug_Conflict_Detector_Crew().crew().kickoff(inputs=inputs)

        print("\n\n=== FINAL REPORT ===\n\n")
        print(result.raw)

        print("Over.")

        output_file_name = "DDI.json"
        source_file = 'output/drug_drug_interaction.json'
        target_path = os.path.join(f"../Blackboard/Contents/{patient_id}/Drug_Drug_Interaction", output_file_name)

        shutil.copy2(source_file, target_path)
        print(f"\n\nReport has been saved to {target_path}")
    

if __name__ == "__main__":
    run()
 



