import logging
from dotenv import load_dotenv

from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.tools.function_tool import FunctionTool
from google.genai import types

from utilities.a2a.agent_discovery import DiscoveryClient
from utilities.a2a.agent_connect import AgentConnector
from llm_config import get_llm_config

logger = logging.getLogger(__name__)
load_dotenv()


class AppointmentAgent:
    def __init__(self):
        self.config = get_llm_config("appointment")
        self.orchestrator = self._build_orchestrator()
        self.user_id = "appointment_user"
        self.runner = Runner(
            app_name=self.orchestrator.name,
            agent=self.orchestrator,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )
        self.discovery = DiscoveryClient()
        self.connectors: dict[str, AgentConnector] = {}

    def _build_orchestrator(self) -> LlmAgent:
        async def list_agents() -> list[dict]:
            cards = await self.discovery.list_agent_cards()
            return [card.model_dump(exclude_none=True) for card in cards]

        async def call_agent(agent_name: str, message: str) -> str:
            cards = await self.discovery.list_agent_cards()
            matched = next((c for c in cards if agent_name.lower() in c.name.lower()), None)
            if not matched:
                raise ValueError(f"Agent '{agent_name}' not found.")
            if matched.name not in self.connectors:
                self.connectors[matched.name] = AgentConnector(matched.name, matched.url)
            connector = self.connectors[matched.name]
            task = await connector.send_task(message, session_id=self.user_id)
            return task.history[-1].parts[0].text if task.history else "No response"

        tools = [FunctionTool(list_agents), FunctionTool(call_agent)]
        return LlmAgent(
            provider=self.config["provider"],
            model=self.config["model"],
            api_key=self.config["api_key"],
            name="appointment_orchestrator",
            description="Handles appointment requests for healthcare.",
            instruction="Use list_agents() and call_agent() to route users to proper specialists.",
            tools=tools
        )

    async def invoke(self, query: str, session_id: str) -> str:
        session = await self.runner.session_service.get_session(
            app_name=self.orchestrator.name,
            user_id=self.user_id,
            session_id=session_id,
        ) or await self.runner.session_service.create_session(
            app_name=self.orchestrator.name,
            user_id=self.user_id,
            session_id=session_id,
            state={},
        )

        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        last_event = None
        async for event in self.runner.run_async(self.user_id, session.id, new_message=content):
            last_event = event
        return "\n".join(p.text for p in last_event.content.parts if p.text) if last_event else ""
