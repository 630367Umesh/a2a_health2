# =============================================================================
# client/client.py (Healthcare Use Case)
# =============================================================================
# Purpose:
# Async client to interact with healthcare agents over A2A protocol.
# - Used to send tasks (e.g., symptom check, appointment booking)
# - Retrieve task history or results
# =============================================================================

import json
from uuid import uuid4
import httpx
from typing import Any

# JSON-RPC models
from models.request import SendTaskRequest, GetTaskRequest
from models.json_rpc import JSONRPCRequest

# Domain models
from models.task import Task, TaskSendParams
from models.agent import AgentCard


# -----------------------------------------------------------------------------
# Custom Exceptions for A2A Client
# -----------------------------------------------------------------------------
class A2AClientHTTPError(Exception):
    """Raised on HTTP failure while communicating with healthcare agent."""
    pass

class A2AClientJSONError(Exception):
    """Raised when the A2A server response is invalid JSON."""
    pass


# -----------------------------------------------------------------------------
# A2AClient: Communicates with healthcare agents via A2A protocol
# -----------------------------------------------------------------------------
class A2AClient:
    def __init__(self, agent_card: AgentCard = None, url: str = None):
        """
        Initialize the client to talk to a healthcare agent via its URL or AgentCard.
        """
        if agent_card:
            self.url = agent_card.url
        elif url:
            self.url = url
        else:
            raise ValueError("You must provide either an AgentCard or a direct URL to the agent.")

    # -------------------------------------------------------------------------
    # Send a user task to the agent
    # -------------------------------------------------------------------------
    async def send_task(self, payload: dict[str, Any]) -> Task:
        """
        Sends a new task (e.g., 'Check my symptoms') to the healthcare agent.

        Args:
            payload (dict): JSON-RPC task payload

        Returns:
            Task: The full task response including history
        """
        request = SendTaskRequest(
            id=uuid4().hex,
            params=TaskSendParams(**payload)
        )

        print("\n📤 Sending task to healthcare agent:")
        print(json.dumps(request.model_dump(), indent=2))

        response = await self._send_request(request)
        return Task(**response["result"])

    # -------------------------------------------------------------------------
    # Fetch a previously sent task (status/history)
    # -------------------------------------------------------------------------
    async def get_task(self, payload: dict[str, Any]) -> Task:
        """
        Fetch task status or response history from a healthcare agent.

        Args:
            payload (dict): must include 'id' or 'sessionId'

        Returns:
            Task: Task object with full history and metadata
        """
        request = GetTaskRequest(params=payload)
        response = await self._send_request(request)
        return Task(**response["result"])

    # -------------------------------------------------------------------------
    # Internal: Perform JSON-RPC HTTP POST
    # -------------------------------------------------------------------------
    async def _send_request(self, request: JSONRPCRequest) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.url,
                    json=request.model_dump(),
                    timeout=60
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise A2AClientHTTPError(e.response.status_code, str(e)) from e

            except json.JSONDecodeError as e:
                raise A2AClientJSONError(str(e)) from e
