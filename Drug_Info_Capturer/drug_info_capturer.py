import os
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

import shutil
import pandas as pd
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
drug_json_searcher = JSONSearchTool('drugbank_clean.json')
input_data = "Lepirudin" 

class DrugConflictDetector(BaseModel):
    DrugName: str
    Drug_Explanation: str
    Drug_Interactions_List: list[str]
    Other_Information: str

class Drug2WebLink():
    # 读取 CSV 文件
    def get_drug_dailymed_link(drug_name: str, csv_file: str = 'fda_drugbank.csv') -> str:
        try:
            df = pd.read_csv(csv_file, encoding='ISO-8859-1', encoding_errors='ignore')
            drug_row = df[df['Drug Name'].str.lower() == drug_name.lower()]
            if not drug_row.empty:
                return drug_row.iloc[0]['DailyMed SPL Link']
            else:
                raise ValueError(f"Drug '{drug_name}' not found in the CSV file.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
        
    def get_drug_fda_link(drug_name: str, csv_file: str = 'fda_drugbank.csv') -> str:
        try:
            df = pd.read_csv(csv_file, encoding='ISO-8859-1', encoding_errors='ignore')
            drug_row = df[df['Drug Name'].str.lower() == drug_name.lower()]
            if not drug_row.empty:
                return drug_row.iloc[0]['DailyMed SPL Link']
            else:
                raise ValueError(f"Drug '{drug_name}' not found in the CSV file.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
    

@CrewBase
class Drug_Conflict_Detector_Crew():
    @agent
    def drug_conflict_detector(self) -> Agent:
        return Agent(
            config = self.agents_config['drug_conflict_detector'],
            tools = [drug_json_searcher],
            verbose = True
        )
    
    @task
    def drug_conflict_detector_task(self) -> Task:
        return Task(
            config = self.tasks_config['drug_conflict_detector_task'],
            output_pydantic = DrugConflictDetector,
            output_file = "output/drug_conflict.json",
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

def run():
        inputs = {
            'drug': input_data
        }

        result = Drug_Conflict_Detector_Crew().crew().kickoff(inputs=inputs)

        print("\n\n=== FINAL REPORT ===\n\n")
        print(result.raw)

        print("Over.")

        drug_name = result.pydantic.DrugName
        print('Drug Name:',drug_name)
        if drug_name:
            file_name = f"{drug_name}_drug_conflict.json"
        else:
            file_name = "drug_conflict.json"
        
        source_file = 'output/drug_conflict.json'
        target_path = os.path.join('drug_confliction',file_name)
        shutil.copy2(source_file, target_path)
        print(f"\n\nReport has been saved to drug_confliction/{file_name}")


if __name__ == "__main__":
    run()
 



