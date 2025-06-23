# =============================================================================
# agents/appointment_agent/task_manager.py
# =============================================================================
# 🎯 Purpose:
# Handles incoming appointment scheduling requests via A2A JSON-RPC protocol.
# 1. Receives a SendTaskRequest
# 2. Extracts user query
# 3. Invokes AppointmentAgent
# 4. Updates task with the agent’s response
# =============================================================================

import logging
from server.task_manager import InMemoryTaskManager
from models.request import SendTaskRequest, SendTaskResponse
from models.task import Message, TaskStatus, TaskState, TextPart
from agents.appointment_agent.agent import AppointmentAgent  # 👈 Updated import

logger = logging.getLogger(_name_)


class AppointmentTaskManager(InMemoryTaskManager):
    """
    🏥 TaskManager that handles appointment scheduling requests by invoking the AppointmentAgent.
    """

    def _init_(self, agent: AppointmentAgent):
        super()._init_()
        self.agent = agent

    def _get_user_text(self, request: SendTaskRequest) -> str:
        return request.params.message.parts[0].text

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        logger.info(f"📩 AppointmentTaskManager received task {request.params.id}")

        task = await self.upsert_task(request.params)
        user_text = self._get_user_text(request)

        # 🧠 Call the orchestrator agent to handle the appointment intent
        agent_reply = await self.agent.invoke(
            user_text,
            request.params.sessionId
        )

        reply_message = Message(
            role="agent",
            parts=[TextPart(text=agent_reply)]
        )

        async with self.lock:
            task.status = TaskStatus(state=TaskState.COMPLETED)
            task.history.append(reply_message)

        return SendTaskResponse(id=request.id, result=task)