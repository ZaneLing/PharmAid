import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from textwrap import dedent
from agents import PatientInfoAgents
from tasks import PatientInfoTasks
from dotenv import load_dotenv

from langchain.tools import DuckDuckGoSearchRun

load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# This is the main class that you will use to define your custom crew.
# You can define as many agents and tasks as you want in agents.py and tasks.py


class PatientInfoCrew:
    def __init__(self, PatientAge, PatientGender, PatientWeight, PatientHeight, PatientBadhabits, PatientOtherInfos):
        self.var1 = PatientAge
        self.var2 = PatientGender
        self.var3 = PatientWeight
        self.var4 = PatientHeight
        self.var5 = PatientBadhabits
        self.var6 = PatientOtherInfos


    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = PatientInfoAgents()
        tasks = PatientInfoTasks()

        # Define your custom agents and tasks here
        custom_agent_1 = agents.Clean_Patient_Info_Agent()
        custom_agent_2 = agents.Analysis_Patient_Info_Agent()

        # Custom tasks include agent name and variables as input
        custom_task_1 = tasks.clean_patient_info_task(
            custom_agent_1,
            self.var1,
            self.var2,
            self.var3,
            self.var4,
            self.var5,
            self.var6,
        )

        custom_task_2 = tasks.analysis_patient_info_task(
            custom_agent_2,
        )

        # Define your custom crew here
        crew = Crew(
            agents=[custom_agent_1, custom_agent_2],
            tasks=[custom_task_1, custom_task_2],
            verbose=True,
            process = Process.sequential,
        )

        result = crew.kickoff()
        return result


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Welcome to PharmAID")
    print("-------------------------------")
    var1 = input(dedent("""Enter patient age: """))
    var2 = input(dedent("""Enter patient gender: """))
    var3 = input(dedent("""Enter patient Height(cm): """))
    var4 = input(dedent("""Enter patient Weight(kg): """))
    var5 = input(dedent("""Enter patient bad habits: """))
    var6 = input(dedent("""Enter other information: """))

    # patientinfocrew = PatientInfoCrew(var1, var2, var3, var4, var5, var6)
    # result_info = patientinfocrew.run()
    # print("result_info: ", result_info)

    custom_crew = PatientInfoCrew(var1, var2, var3, var4, var5, var6)
    result = custom_crew.run()
    print("\n\n########################")
    print("## Here is the analysis of the patient:")
    print("########################\n")
    print(result)
    print(f"Token Usage: {result.token_usage}")