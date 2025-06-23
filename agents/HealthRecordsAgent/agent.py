from crewai import Agent, Task, Crew
from crewai_tools import tool
from dotenv import load_dotenv
from llm_config import get_llm_config
import os

load_dotenv()
config = get_llm_config("healthrecords")

# Define tools
@tool
def fetch_patient_record(patient_id: str) -> str:
    mock_db = {
        "101": "Patient 101: Diabetes Type 2, on Metformin.",
        "102": "Patient 102: Hypertension, last visit: May 2025.",
        "103": "Patient 103: No known conditions, annual checkup due."
    }
    return mock_db.get(patient_id, "No record found for this ID.")

@tool
def update_patient_note(patient_id: str, note: str) -> str:
    return f"Note added to patient {patient_id}: '{note}'"

# CrewAI agent
health_records_agent = Agent(
    role="Health Records Manager",
    goal="Manage secure patient records using EMR tools.",
    backstory="A trusted digital assistant for doctors and staff to maintain health records.",
    tools=[fetch_patient_record, update_patient_note],
    verbose=True,
    llm={
        "provider": config["provider"],
        "model": config["model"],
        "api_key": config["api_key"]
    }
)

def create_health_records_tasks(patient_id: str, note: str = None):
    tasks = [
        Task(
            description=f"Fetch health records for patient ID {patient_id}.",
            expected_output="Accurate patient summary.",
            agent=health_records_agent
        )
    ]
    if note:
        tasks.append(
            Task(
                description=f"Add note: '{note}' to patient ID {patient_id}.",
                expected_output="Confirmation that note was added.",
                agent=health_records_agent
            )
        )
    return tasks

if __name__ == "__main__":
    crew = Crew(
        agents=[health_records_agent],
        tasks=create_health_records_tasks("101", "Follow-up scheduled for July."),
        verbose=True
    )
    print(crew.run())
