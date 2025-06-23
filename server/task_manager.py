# =============================================================================
# task_manager.py — Healthcare Agent Task Manager (CrewAI + A2A)
# =============================================================================

from abc import ABC, abstractmethod
from typing import Dict
import asyncio

from models.request import SendTaskRequest, SendTaskResponse, GetTaskRequest, GetTaskResponse
from models.task import Task, TaskSendParams, TaskQueryParams, TaskStatus, TaskState, Message

# Import your CrewAI/LLM logic here — e.g., build_agent_response() should handle agent output
from agent.core import build_agent_response  # 👈 Replace with your actual CrewAI agent runner


# -----------------------------------------------------------------------------
# Abstract Base Class
# -----------------------------------------------------------------------------

class TaskManager(ABC):
    @abstractmethod
    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        pass

    @abstractmethod
    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        pass


# -----------------------------------------------------------------------------
# Healthcare Task Manager (In-Memory + LLM Orchestration)
# -----------------------------------------------------------------------------

class HealthcareTaskManager(TaskManager):
    """
    This Task Manager uses CrewAI to process tasks in memory and respond based on
    the healthcare agent's logic (SymptomChecker, Appointment, or HealthRecords).
    """

    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.lock = asyncio.Lock()

    async def upsert_task(self, params: TaskSendParams) -> Task:
        async with self.lock:
            task = self.tasks.get(params.id)

            if task is None:
                task = Task(
                    id=params.id,
                    status=TaskStatus(state=TaskState.SUBMITTED),
                    history=[params.message]
                )
                self.tasks[params.id] = task
            else:
                task.history.append(params.message)

            return task

    async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
        params = request.params
        user_message = params.message.parts[0].text

        # ⬇️ Store user message + create/update task
        task = await self.upsert_task(params)

        # 🤖 Generate reply using CrewAI agent logic (customize per agent)
        try:
            agent_reply = await build_agent_response(user_message)  # CrewAI output (text)
        except Exception as e:
            agent_reply = f"Sorry, an internal error occurred: {e}"

        # 🧾 Record agent response
        agent_msg = Message(role="agent", parts=[{"type": "text", "text": agent_reply}])
        async with self.lock:
            task.history.append(agent_msg)
            task.status.state = TaskState.COMPLETED

        return SendTaskResponse(id=request.id, result=task)

    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        async with self.lock:
            query: TaskQueryParams = request.params
            task = self.tasks.get(query.id)

            if not task:
                return GetTaskResponse(id=request.id, error={"message": "Task not found"})

            task_copy = task.model_copy()
            if query.historyLength is not None:
                task_copy.history = task_copy.history[-query.historyLength:]

            return GetTaskResponse(id=request.id, result=task_copy)
