import logging
import click
import uvicorn

from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentCapability, AgentSkill
from agents.symptom_checker_agent.agent import SymptomCheckerAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", default="localhost", help="Host to bind SymptomCheckerAgent server")
@click.option("--port", default=10020, help="Port to bind SymptomCheckerAgent server")
def main(host: str, port: int):
    logger.info(f"🩺 Starting SymptomCheckerAgent on http://{host}:{port}/")

    agent_logic = SymptomCheckerAgent()

    agent_card = AgentCard(
        id="symptom_checker_agent",
        name="Symptom Checker Agent",
        description="Analyzes symptoms and delegates to appropriate specialists.",
        url=f"http://{host}:{port}/",
        capabilities=AgentCapabilities(capabilities=[
            AgentCapability(
                type="symptom-checking",
                name="Check Symptoms",
                description="Analyze symptoms and route to specialists.",
                skills=[
                    AgentSkill(
                        name="check_symptoms",
                        description="Checks symptoms and delegates to specialists"
                    )
                ]
            )
        ])
    )

    server = A2AServer(agent_card=agent_card, task_manager=agent_logic)
    uvicorn.run(server.app, host=host, port=port)

if __name__ == "__main__":
    main()
