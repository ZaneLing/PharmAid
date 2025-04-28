from crewai import Agent
from textwrap import dedent
from langchain.llms import OpenAI, Ollama
from langchain_openai import ChatOpenAI

class PatientInfoAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    def Clean_Patient_Info_Agent(self):
        return Agent(
            role="Patient Infomation Cleaner",
            backstory=dedent(f"""You are a data scientist working on a project to clean patient information into a list"""),
            goal=dedent(f"""Clean the patient information into a list"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )

    def Analysis_Patient_Info_Agent(self):
        return Agent(
            role="Analyze the patient information",
            backstory=dedent(f"""You are a pharmcy doctor.You have to analyze patient information."""),
            goal=dedent(f"""Pharmacy analysis of the patient's basic condition."""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )

class DrugInteractionAgents:
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    def DrugContentLister(self):
        return Agent(
            role="Drug Content Lister",
            backstory=dedent(f"""You are a pharmacist. You have to list the contents of this drug"""),
            goal=dedent(f"""List the contents of this drug"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )

    def DrugConflictLister(self):
        return Agent(
            role="Drug Conflict Lister",
            backstory=dedent(f"""You are a pharmacist. You have to list the drugs with the reasons that conflice with this drug"""),
            goal=dedent(f"""List conflict drugs"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )
    
    def DrugConflictDetector(self):
        return Agent(
            role="Double Drug Conflict Detector",
            backstory=dedent(f"""You are a pharmacist. You have to check conflict among thess drugs"""),
            goal=dedent(f"""Check conflict in this drug list"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )
    
class PresicriptionAgents:
    """
        This class defines the agents for the prescription writing process.
        Functions include:
        ·Drug selection
        ·Dose recommendation
        ·Medication instructions
        ·Matters attention
    """
    def __init__(self):
        self.OpenAIGPT35 = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    def DrugSelector(self):
        return Agent(
            role="Drug Selector",
            backstory=dedent(f"""You are a pharmacist. You have to select the drug"""),
            goal=dedent(f"""Select the drug"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )

    def DoseRecommender(self):
        return Agent(
            role="Dose Recommender",
            backstory=dedent(f"""You are a pharmacist. You have to recommend the dose"""),
            goal=dedent(f"""Recommend the dose"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )
    
    def MedicationInstructor(self):
        return Agent(
            role="Medication Instructor",
            backstory=dedent(f"""You are a pharmacist. You have to instruct the medication"""),
            goal=dedent(f"""Instruct the medication"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )
    
    def AttentionMatter(self):  
        return Agent(
            role="Attention Matter",
            backstory=dedent(f"""You are a pharmacist. You have to pay attention to the matters"""),
            goal=dedent(f"""Pay attention to the matters"""),
            # tools=[tool_1, tool_2],
            allow_delegation=False,
            verbose=True,
            llm=self.OpenAIGPT35,
        )