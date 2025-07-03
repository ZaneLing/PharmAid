import os
import shutil
from crewai import Agent, Crew, Task, Process, LLM
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from langchain_openai import ChatOpenAI
from textwrap import dedent
import sys
from pydantic import BaseModel
from dotenv import load_dotenv
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# load_dotenv()
# oak = os.getenv("OPENAI_API_KEY")
# os.environ["OPENAI_API_KEY"] = oak

from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool,
    TXTSearchTool,
)

# Instantiate tools
# docs_tool = DirectoryReadTool(directory='../CCMDataset/L1/1058')
# file_tool = FileReadTool()
# file_search_tool = TXTSearchTool(txt='../CCMDataset/L1/1058.txt')


# 定义输出数据模型
class PatientInformation(BaseModel):
    Chief_Complaint: str    #用于产生initial prescription
    Allergies: list[str]      #DPI
    History_of_Present_Illness: list[str]   #DPI
    Past_Medical_History: list[str]  #DDI
    Social_history: list[str]   #DPI
    Family_history: list[str]   #DPI
    Physical_Exam: list[str]    #DPI
    Medications_on_Admissions: list[str]   #DDI
    Discharge_Diagnose: list[str]       #用于产生initial prescription
    Discharge_Medications: list[str]     #暂时不用，retro用的
    Other_Discharge_Information: list[str]     #暂时不用，retro用的

@CrewBase
class Patient_Info_Crew():
    # @agent
    # def patient_info_cleaner(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['patient_info_cleaner'],
    #         tools=[file_search_tool],
    #         verbose=True
    #     )
    
    @agent
    def Patient_Info_Cleaner(self) -> Agent:
        return Agent(
            config=self.agents_config['Patient_Info_Cleaner'],
            verbose=True,
            llm=LLM(model="ollama/qwen3:8b", base_url="http://localhost:11434"),
            #llm=LLM(model="ollama/llama3.1:8b-instruct-q4_0", base_url="http://localhost:11434"),
            #llm=LLM(model="ollama/deepseek-r1:8b", base_url="http://localhost:11434"),

        )
    
    @task
    def Patient_Info_Clean_Task(self) -> Task:
        return Task(
            config=self.tasks_config['Patient_Info_Clean_Task'],
            output_pydantic=PatientInformation,
            output_file="output/patient_info.json",
        )

    # @task
    # def patient_info_cleaner_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['patient_info_cleaner_task'],
    #         output_pydantic=PatientInformation,
    #         output_file="output/patient_info.json",
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
def load_input_text(file_path):
    """
    从指定文件路径读取文本内容。
    :param file_path: 文本文件路径
    :return: 文件内容字符串
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            print(f"[INFO] 成功读取文件内容: {file_path}")
            return content
    except Exception as e:
        print(f"[ERROR] 无法读取文件 {file_path}: {e}")
        return ""
    
def run():
    CCMDATA_PATH = os.path.join(PROJECT_ROOT, "CCMDataset/L1/1058.txt")
    input_text = load_input_text("../CCMDataset/L1/1058.txt")

    if not input_text:
        print("[ERROR] 输入文本为空，无法继续执行。")
        return
    
    print("--------------------------")
    print(input_text)

    inputs = {
        'text':input_text
    }
    result = Patient_Info_Crew().crew().kickoff(inputs=inputs)
    
    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")

    

def patient_info_clean_process(folder_path):
    #输入是一个文件夹路径
    try:
        files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
        if not files:
            print(f"[Error] 文件夹 {folder_path} 中没有找到文本文件。")
            return

        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                input_data = file.read().strip()  # 读取文件内容

            print(f"\n[---------Processing File----------] {file_name}")

            inputs = {
                'text':input_data
            }
            #result = Patient_Info_Crew().crew().kickoff(inputs=inputs)
            result = Patient_Info_Crew().crew().kickoff(inputs=inputs)

            print("\n\n=== FINAL REPORT ===\n\n")
            print(result.raw)

            # 提取文件名并保存结果
            base_name = os.path.splitext(file_name)[0]
            output_file_name = f"{base_name}_patient_info.json"
            source_file = 'output/patient_info.json'
            target_path = os.path.join('patient_info_reports', output_file_name)

            os.makedirs('patient_info_reports', exist_ok=True)
            shutil.copy2(source_file, target_path)

            print(f"\n\nReport has been saved to {target_path}")

            print(f"[INFO] 处理患者 ID: {base_name}")
            #input_file = ".../Patient_Info_Cleaner/patient_info_reports/{patient_id}_patient_info.json"  # 替换为你的 JSON 文件路径
            #input_file = ".../Patient_Info_Cleaner/patient_info_reports/1_patient_info.json"
            in_file = f'patient_info_reports/{base_name}_patient_info.json'  # 替换为你的 JSON 文件路径
            # 输出文件夹路径
            output_folder = f'./BlackBoard/Contents/{base_name}/Patient_Info'  # 替换为你的输出文件夹路径
            split_json_by_subtitles(in_file, output_folder)

    except Exception as e:
        print(f"[Error] 处理文件夹 {folder_path} 时出错: {e}")

import os
import json

def split_json_by_subtitles(input_file, output_folder):
    try:
        # 读取输入 JSON 文件
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 确保输出文件夹存在
        os.makedirs(output_folder, exist_ok=True)

        # 遍历 JSON 数据的每个子标题
        for subtitle, content in data.items():
            # 构造输出文件路径
            output_file = os.path.join(output_folder, f"{subtitle}.json")

            # 将子标题内容写入单独的 JSON 文件
            with open(output_file, 'w', encoding='utf-8') as outfile:
                json.dump({subtitle: content}, outfile, ensure_ascii=False, indent=4)

            print(f"[INFO] 已保存: {output_file}")

    except Exception as e:
        print(f"[ERROR] 处理文件时出错: {e}")


    

if __name__ == "__main__":
    # 示例：运行单个输入
    #run()

    if len(sys.argv) != 2:
        print("[Error] 请提供Dataset参数，例如: python prescription.py ./dataset/1058.txt")
        sys.exit(1)

    folder_path = sys.argv[1]
    

    # # 示例：从文件夹读取输入并运行
    #folder_path = "../CCMDataset/L1"  # 替换为你的文件夹路径
    patient_info_clean_process(folder_path)

    # patient_id = 1  # 替换为你的患者 ID
    # print(f"[INFO] 处理患者 ID: {patient_id}")
    
    # #input_file = ".../Patient_Info_Cleaner/patient_info_reports/{patient_id}_patient_info.json"  # 替换为你的 JSON 文件路径
    # #input_file = ".../Patient_Info_Cleaner/patient_info_reports/1_patient_info.json"
    # input_file = '/Users/lingziyang/Desktop/PharmAid-main/Patient_Info_Cleaner/patient_info_reports/1_patient_info.json'  # 替换为你的 JSON 文件路径
    # # 输出文件夹路径
    # output_folder = f'.../BlackBoard/Contents/{patient_id}'  # 替换为你的输出文件夹路径

    # split_json_by_subtitles(input_file, output_folder)