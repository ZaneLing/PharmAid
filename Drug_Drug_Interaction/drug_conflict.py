import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

from textwrap import dedent
from agents import PatientInfoAgents, DrugInteractionAgents
from tasks import PatientInfoTasks, DrugInteractionTasks
from dotenv import load_dotenv

from langchain.tools import DuckDuckGoSearchRun

load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# This is the main class that you will use to define your custom crew.
# You can define as many agents and tasks as you want in agents.py and tasks.py


class DrugConflictCrew:
    def __init__(self, AimDrug):
        self.var1 = AimDrug

    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = DrugInteractionAgents()
        tasks = DrugInteractionTasks()

        # Define your custom agents and tasks here
        druglistagent_1 = agents.DrugContentLister()
        druglistagent_2 = agents.DrugConflictLister()

        # Custom tasks include agent name and variables as input
        drug_list_task_1 = tasks.drug_ingredient_lister_task(
            druglistagent_1,
            self.var1,
        )

        drug_list_task_2 = tasks.drug_conflict_lister_task(
            druglistagent_2,
            self.var1,
        )

        # Define your custom crew here
        crew = Crew(
            agents=[druglistagent_1, druglistagent_2],
            tasks=[drug_list_task_1, drug_list_task_2],
            verbose=True,
            process=Process.sequential,
        )

        result = crew.kickoff()
        return result


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Welcome to PharmAID")
    print("-------------------------------")
    var1 = input(dedent("""Enter single drug: """))

    # patientinfocrew = PatientInfoCrew(var1, var2, var3, var4, var5, var6)
    # result_info = patientinfocrew.run()
    # print("result_info: ", result_info)

    custom_crew = DrugConflictCrew(var1)
    result = custom_crew.run()
    print("\n\n########################")
    print("## Here is the analysis of this drug:")
    print("########################\n")
    print(result)
