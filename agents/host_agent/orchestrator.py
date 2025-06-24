# agents/host_agent/orchestrator.py

import uuid
import logging

from models.agent import AgentCard, AgentCapabilities, AgentCapability, AgentSkill
from server import A2AServer
from agents.host_agent.task_manager import TaskManager
from utilities.a2a.agent_discovery import AgentDiscovery

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self):
        self.agent_card = AgentCard(
            id=str(uuid.uuid4()),
            name="OrchestratorAgent",
            description="Routes tasks to the appropriate healthcare agents",
            url="http://localhost:10000",
            capabilities=AgentCapabilities(
                capabilities=[
                    AgentCapability(
                        type="routing",
                        skills=[
                            AgentSkill(name="delegate_to_symptom_agent"),
                            AgentSkill(name="connect_health_records"),
                            AgentSkill(name="book_appointments")
                        ]
                    )
                ]
            )
        )

        self.discovery = AgentDiscovery("agent_registry.json")
        self.task_manager = TaskManager(discovery=self.discovery)
        self.server = A2AServer(
            host="localhost",
            port=10000,
            agent_card=self.agent_card,
            task_manager=self.task_manager
        )

    async def start(self):
        logger.info(f"🚀 Starting OrchestratorAgent on {self.agent_card.url}")
        await self.server.start()
