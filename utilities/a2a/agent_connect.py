# =============================================================================
# utilities/a2a/agent_connect.py
# =============================================================================
# 🎯 Purpose:
# Provides an async wrapper (`AgentConnector`) to delegate healthcare tasks
# to remote A2A agents (e.g., SymptomCheckerAgent, AppointmentAgent, etc.)
# =============================================================================

import uuid
import logging

from client.client import A2AClient               # Handles JSON-RPC communication
from models.task import Task                      # Task model for result typing

logger = logging.getLogger(__name__)


class AgentConnector:
    """
    🔗 Connects to a remote A2A healthcare agent (Symptom, Appointment, HealthRecords, etc.)

    Attributes:
        name (str): Descriptive name of the healthcare agent.
        client (A2AClient): Client initialized with agent's base URL.
    """

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.client = A2AClient(url=base_url)
        logger.info(f"[AgentConnector] Initialized: {self.name} -> {base_url}")

    async def send_task(self, message: str, session_id: str, metadata: dict = None) -> Task:
        """
        Sends a user task (e.g., symptoms or appointment intent) to the agent.

        Args:
            message (str): Message content from the user.
            session_id (str): Unique session ID to group related interactions.
            metadata (dict, optional): Extra context (e.g., patient ID, specialization).

        Returns:
            Task: The full result Task returned from the agent.
        """
        task_id = uuid.uuid4().hex

        payload = {
            "id": task_id,
            "sessionId": session_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}]
            },
            "metadata": metadata or {}
        }

        try:
            result = await self.client.send_task(payload)
            logger.info(f"[AgentConnector] Task completed from {self.name} (ID: {task_id})")
            return result
        except Exception as e:
            logger.error(f"[AgentConnector] Error from {self.name}: {e}")
            raise
