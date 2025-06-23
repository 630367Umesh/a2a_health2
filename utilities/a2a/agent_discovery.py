import json
import logging
from pathlib import Path
from models.agent import AgentCard

logger = logging.getLogger(__name__)

class AgentDiscovery:
    def __init__(self, registry_path="agent_registry.json"):
        self.registry_path = Path(registry_path)
        self.agents = []

    async def discover_agents(self):
        try:
            logger.info("[Discovery] Looking for agents...")
            if not self.registry_path.exists():
                logger.warning("[Discovery] Registry file not found.")
                return []

            with open(self.registry_path, "r") as f:
                data = json.load(f)

            self.agents = [AgentCard(**agent) for agent in data.get("agents", [])]
            logger.info(f"[Discovery] Found {len(self.agents)} agents")
            return self.agents

        except Exception as e:
            logger.error(f"[Discovery] Failed to parse registry: {e}")
            return []

    def get_agents(self):
        return self.agents
