import logging
from dotenv import load_dotenv

from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.tools.function_tool import FunctionTool
from google.genai import types

from utilities.a2a.agent_discovery import AgentDiscovery
from utilities.a2a.agent_connect import AgentConnector
from agents.llm_config import get_llm_config

logger = logging.getLogger(__name__)
load_dotenv()

class SymptomCheckerAgent:
    def __init__(self):
        # ✅ Load config with model only — don't pass provider/api_key to LlmAgent
        self.config = get_llm_config("symptom_checker")
        self.model = self.config.get("model")

        if not self.model:
            raise ValueError("Missing model in config.")

        self.discovery = AgentDiscovery()
        self.connectors: dict[str, AgentConnector] = {}
        self.orchestrator = self._build_orchestrator()
        self.user_id = "symptom_user"
        self.runner = Runner(
            app_name=self.orchestrator.name,
            agent=self.orchestrator,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

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
                self.connectors[matched.name] = AgentConnector(name=matched.name, base_url=matched.url)
            connector = self.connectors[matched.name]
            task = await connector.send_task(message, session_id=self.user_id)
            return task.history[-1].parts[0].text if task.history else "No response"

        system_instruction = (
            "You are a Symptom Checker Assistant. "
            "Your job is to:\n"
            "- Analyze a user's symptoms\n"
            "- Suggest a probable condition OR\n"
            "- Route the user to an appropriate specialist by calling list_agents() "
            "and then call_agent(agent_name, message).\n\n"
            "Example:\n"
            "If a user says 'I have skin rashes', call list_agents(), find 'Dermatologist', "
            "and delegate with call_agent()."
        )

        tools = [FunctionTool(list_agents), FunctionTool(call_agent)]

        return LlmAgent(
            model=self.model,
            name="symptom_checker_orchestrator",
            description="Analyzes symptoms and delegates to appropriate healthcare agents.",
            instruction=system_instruction,
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

        if not last_event or not last_event.content or not last_event.content.parts:
            return "No response generated."

        return "\n".join([p.text for p in last_event.content.parts if p.text])
