import os
import shutil
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from textwrap import dedent
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

from crewai_tools import XMLSearchTool

XML_Searcher = XMLSearchTool('drug_adr_xml')

input_data = "Lepirudin"  # 示例药物名称

# 定义输出数据模型
class DrugADRDetector(BaseModel):
    DrugName: str
    ADR_List: list[str]  # 不良反应列表
    Source: str  # 数据来源

@CrewBase
class Drug_ADR_Detector_Crew():
    @agent
    def drug_adr_detector(self) -> Agent: 
        return Agent(
            config=self.agents_config['drug_adr_detector'],
            tools=[XML_Searcher],
            verbose=True
        )
    
    @task
    def drug_adr_detector_task(self) -> Task:
        return Task(
            config=self.tasks_config['drug_adr_detector_task'],
            output_pydantic=DrugADRDetector,
            output_file="output/drug_adr.json",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

def run():
    # 输入药物名称
    inputs = {
        'drug': input_data
    }

    # 执行 Crew
    result = Drug_ADR_Detector_Crew().crew().kickoff(inputs=inputs)

    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")

    # 提取药物名称
    drug_name = result.pydantic.DrugName
    print('Drug Name:', drug_name)
    if drug_name:
        file_name = f"{drug_name}_drug_adr.json"
    else:
        file_name = "drug_adr.json"
    
    # 保存结果到指定文件夹
    source_file = 'output/drug_adr.json'
    target_path = os.path.join('drug_adr_reports', file_name)
    os.makedirs('drug_adr_reports', exist_ok=True)
    shutil.copy2(source_file, target_path)
    print(f"\n\nReport has been saved to drug_adr_reports/{file_name}")

def run_with_file_input(folder_path):
    try:
        # 获取文件夹中的所有文本文件
        files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        if not files:
            print(f"[Error] 文件夹 {folder_path} 中没有找到文本文件。")
            return

        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                input_data = file.read().strip()  # 读取药物名称

            print(f"\n[Processing File] {file_name} - Drug: {input_data}")

            # 执行 Crew
            inputs = {'drug': input_data}
            result = Drug_ADR_Detector_Crew().crew().kickoff(inputs=inputs)

            print("\n\n=== FINAL REPORT ===\n\n")
            print(result.raw)

            # 提取药物名称
            drug_name = result.pydantic.DrugName
            print('Drug Name:', drug_name)
            if drug_name:
                file_name = f"{drug_name}_drug_adr.json"
            else:
                file_name = "drug_adr.json"
            
            # 保存结果到指定文件夹
            source_file = 'output/drug_adr.json'
            target_path = os.path.join('drug_adr_reports', file_name)
            os.makedirs('drug_adr_reports', exist_ok=True)
            shutil.copy2(source_file, target_path)
            print(f"\n\nReport has been saved to drug_adr_reports/{file_name}")

    except Exception as e:
        print(f"[Error] 处理文件夹 {folder_path} 时出错: {e}")

if __name__ == "__main__":
    # run()

    folder_path = 'CompositeCaseMedicationDataset/L1'
    run_with_file_input(folder_path)