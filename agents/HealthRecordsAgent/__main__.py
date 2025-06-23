# agents/health_records_agent/__main__.py

import logging
import click

from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.health_records_agent.task_manager import HealthRecordsTaskManager
from agents.health_records_agent.agent import health_records_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind HealthRecordsAgent server to")
@click.option("--port", default=10030, help="Port for HealthRecordsAgent server")
def main(host: str, port: int):
    print(f"\n📋 Starting HealthRecordsAgent on http://{host}:{port}/\n")

    capabilities = AgentCapabilities(streaming=False)

    skill = AgentSkill(
        id="manage_health_records",
        name="Health Records Manager",
        description="Retrieves and updates patient health records securely.",
        tags=["healthcare", "EMR", "records"],
        examples=[
            "Get record for patient 101",
            "Add note to 102: Patient is recovering"
        ]
    )

    agent_card = AgentCard(
        name="HealthRecordsAgent",
        description="Agent that manages patient health records using CrewAI.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[skill],
    )

    task_manager = HealthRecordsTaskManager(agent=health_records_agent)

    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    server.start()

if __name__ == "__main__":
    main()
