import asyncio
import uuid
import logging

from utilities.a2a.agent_discovery import AgentDiscovery
from agents.host_agent.task_manager import TaskManager
from models.agent import AgentCard, AgentCapability
from server import A2AServer

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    def __init__(self):
        self.agent_card = AgentCard(
            id=str(uuid.uuid4()),
            name="OrchestratorAgent",
            description="Routes tasks to the appropriate healthcare agents",
            capabilities=[
                AgentCapability(name="routing", description="Routes task to other agents"),
                AgentCapability(name="mcp", description="Supports Model Context Protocol"),
                AgentCapability(name="a2a", description="Uses Agent-to-Agent Protocol")
            ],
            tools=[{"name": "route_task", "description": "Route task to appropriate agent"}]
        )

        self.discovery = AgentDiscovery(registry_path="agent_registry.json")
        self.task_manager = TaskManager(discovery=self.discovery)
        self.server = A2AServer(
            host="0.0.0.0",
            port=5000,
            agent_card=self.agent_card,
            task_manager=self.task_manager
        )

    async def start(self):
        logger.info("Starting OrchestratorAgent...")
        await self.server.start()
