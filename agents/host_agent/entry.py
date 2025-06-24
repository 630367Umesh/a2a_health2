import logging
import click
import asyncio

from agents.host_agent.orchestrator import OrchestratorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.command()
@click.option('--host', default='localhost', help='Host to bind the agent')
@click.option('--port', default=10000, help='Port to bind the agent')
def main(host, port):
    logger.info(f"🚀 Starting OrchestratorAgent on http://{host}:{port}/")
    agent = OrchestratorAgent()
    asyncio.run(agent.start())

if __name__ == "__main__":
    main()
