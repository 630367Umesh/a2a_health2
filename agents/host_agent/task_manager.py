# agents/host_agent/task_manager.py

import logging
from utilities.a2a.agent_connect import AgentConnector

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self, discovery):
        self.discovery = discovery

    async def handle_task(self, task):
        """
        Route the task to the appropriate healthcare agent based on intent.
        """
        message = task.message.parts[0].text.lower()
        session_id = task.session_id

        logger.info(f"[TaskManager] Routing message: {message}")

        if any(keyword in message for keyword in ["fever", "headache", "cough", "pain"]):
            return await self._delegate("SymptomCheckerAgent", message, session_id)

        elif "appointment" in message or "book" in message:
            return await self._delegate("AppointmentAgent", message, session_id)

        elif "record" in message or "history" in message:
            return await self._delegate("HealthRecordsAgent", message, session_id)

        else:
            logger.warning("[TaskManager] Unrecognized task. Defaulting to SymptomCheckerAgent.")
            return await self._delegate("SymptomCheckerAgent", message, session_id)

    async def _delegate(self, agent_name: str, message: str, session_id: str):
        """Use AgentConnector to send task to remote agent."""
        agent = self.discovery.find_by_name(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in registry")

        connector = AgentConnector(name=agent_name, base_url=agent.url)
        return await connector.send_task(message, session_id)
