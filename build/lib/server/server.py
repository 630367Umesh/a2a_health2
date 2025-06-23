# =============================================================================
# server.py — Healthcare Agent2Agent Server
# =============================================================================
# Purpose:
# A Starlette-powered JSON-RPC 2.0 server for handling healthcare-related tasks.
# Supports:
# ✅ Accepting tasks from clients/agents (POST /)
# ✅ Agent discovery metadata (GET /.well-known/agent.json)
# =============================================================================

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request

from models.agent import AgentCard
from models.request import A2ARequest, SendTaskRequest
from models.json_rpc import JSONRPCResponse, InternalError

from server import task_manager  # Your actual agent logic (Gemini, CrewAI etc.)

import json
import logging
from datetime import datetime
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger(__name__)


def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Unsupported type: {type(obj)}")


class A2AServer:
    def __init__(self, host="0.0.0.0", port=5000, agent_card: AgentCard = None, task_manager: task_manager = None):
        """
        Initializes the Healthcare A2A Server.

        Args:
            host: Bind address (default: all interfaces)
            port: HTTP port (default: 5000)
            agent_card: Agent identity metadata (name, skills, capabilities)
            task_manager: The CrewAI/Gemini-backed handler for incoming tasks
        """
        self.host = host
        self.port = port
        self.agent_card = agent_card
        self.task_manager = task_manager

        self.app = Starlette()
        self.app.add_route("/", self._handle_request, methods=["POST"])
        self.app.add_route("/.well-known/agent.json", self._get_agent_card, methods=["GET"])

    def start(self):
        if not self.agent_card or not self.task_manager:
            raise ValueError("AgentCard and TaskManager are required to start server.")

        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)

    def _get_agent_card(self, request: Request) -> JSONResponse:
        """
        Responds to GET /.well-known/agent.json with agent metadata.

        Useful for discovery by orchestrators like AppointmentAgent.
        """
        return JSONResponse(self.agent_card.model_dump(exclude_none=True))

    async def _handle_request(self, request: Request):
        """
        Handles POST requests for tasks using JSON-RPC 2.0.

        Expects `SendTaskRequest`, delegates it to the task_manager.
        Returns: JSON-RPC-compliant result or error.
        """
        try:
            body = await request.json()
            print("\n📨 Incoming JSON-RPC Request:", json.dumps(body, indent=2))

            json_rpc = A2ARequest.validate_python(body)

            if isinstance(json_rpc, SendTaskRequest):
                result = await self.task_manager.on_send_task(json_rpc)
            else:
                raise ValueError(f"Unsupported A2A method: {type(json_rpc)}")

            return self._create_response(result)

        except Exception as e:
            logger.error(f"❌ Exception in server: {e}")
            return JSONResponse(
                JSONRPCResponse(id=None, error=InternalError(message=str(e))).model_dump(),
                status_code=400
            )

    def _create_response(self, result):
        """
        Converts a valid JSONRPCResponse object to a Starlette response.
        """
        if isinstance(result, JSONRPCResponse):
            return JSONResponse(content=jsonable_encoder(result.model_dump(exclude_none=True)))
        else:
            raise ValueError("Invalid response type")
