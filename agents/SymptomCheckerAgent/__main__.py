import logging
import click
from agents.SymptomCheckerAgent.agent import SymptomCheckerAgent
from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.SymptomCheckerAgent.agent import SymptomCheckerAgent
from agents.SymptomCheckerAgent.task_manager import SymptomCheckerTaskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind SymptomCheckerAgent server to")
@click.option("--port", default=10020, help="Port for SymptomCheckerAgent server")
def main(host: str, port: int):
    print(f"\n🩺 Starting SymptomCheckerAgent on http://{host}:{port}/\n")

    capabilities = AgentCapabilities(streaming=False)
    skill = AgentSkill(
        id="check_symptoms",
        name="Symptom Checker",
        description="Analyzes symptoms and suggests potential conditions",
        tags=["healthcare", "diagnosis", "symptoms"],
        examples=["I have a fever and sore throat", "Why does my back hurt?"]
    )

    agent_card = AgentCard(
        name="SymptomCheckerAgent",
        description="Agent that checks symptoms and suggests potential health issues.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[skill]
    )

    agent = SymptomCheckerAgent()
    task_manager = SymptomCheckerTaskManager(agent)

    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    server.start()

if __name__ == "__main__":
    main()
