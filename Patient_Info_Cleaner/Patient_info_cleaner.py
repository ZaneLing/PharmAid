import os
import shutil
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from langchain_openai import ChatOpenAI
from textwrap import dedent
from pydantic import BaseModel
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# 示例输入数据
input_data = "My name is Li Fang, 42 years old, teacher. In the past two months, I have sustained back pain (aggravated by sitting/standing for a long time), stomach distension and acid reflux after meals, numbness in my right hand, and weight inexplicably dropped 3 kilograms. Irregular diet (often do not eat breakfast, dinner takeout greasy), lack of exercise, stay up late to prepare classes until 22 o 'clock, poor sleep (about 1 hour to sleep), 10 years of smoking history (now changed to electronic cigarettes). The mother suffers from diabetes, and the blood lipid in the physical examination last year has not been treated."

# 定义输出数据模型
class PatientInformation(BaseModel):
    Patient_demographics: list[str]
    Diagnoses: list[str]
    Allergy_history_past_medical_history: list[str]
    Current_medications: list[str]
    History_of_present_illness: list[str]
    Inspection_findings: list[str]
    Other_relevant_information_before_the_admission: list[str]

@CrewBase
class Patient_Info_Crew():
    @agent
    def patient_info_cleaner(self) -> Agent:
        return Agent(
            config=self.agents_config['patient_info_cleaner'],
            verbose=True
        )

    @task
    def patient_info_cleaner_task(self) -> Task:
        return Task(
            config=self.tasks_config['patient_info_cleaner_task'],
            output_pydantic=PatientInformation,
            output_file="output/patient_info.json",
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
        'statement': input_data
    }

    result = Patient_Info_Crew().crew().kickoff(inputs=inputs)
    
    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("Over.")

    source_file = 'output/patient_info.json'

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

            print(f"\n[Processing File] {file_name}")

            # 执行 Crew
            inputs = {'statement': input_data}
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

    except Exception as e:
        print(f"[Error] 处理文件夹 {folder_path} 时出错: {e}")

if __name__ == "__main__":
    # 示例：运行单个输入
    # run()

    # 示例：从文件夹读取输入并运行
    folder_path = "../CCMDataset/L1"  # 替换为你的文件夹路径
    patient_info_clean_process(folder_path)