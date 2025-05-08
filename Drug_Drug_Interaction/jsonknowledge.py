from crewai import Agent, Task, Crew, Process, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

# Create a knowledge source

from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource

# Create a JSON knowledge source
json_source = JSONKnowledgeSource(
    file_paths=["drugbank_clean.json"]
)
import os
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

import shutil

from textwrap import dedent
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()
oak = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = oak

# Create an LLM with a temperature of 0 to ensure deterministic outputs
llm = LLM(model="gpt-3.5-turbo", temperature=0)

# Create an agent with the knowledge store
agent = Agent(
    role="Pharmacist",
    goal="You have to know everything about the drug.",
    backstory="""You are a master at understanding drugs and their interactions.""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

task = Task(
    description="Answer the following questions about the user: {question}",
    expected_output="An answer to the question about the drug.",
    agent=agent,
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True,
    process=Process.sequential,
    knowledge_sources=[json_source], # Enable knowledge by adding the sources here. You can also add more sources to the sources list.
)

result = crew.kickoff(inputs={"question": "A List of the confilction drugs of Lepirudin"})

print(result.raw)