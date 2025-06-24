# agents/symptom_checker_agent/task_manager.py

from typing import Dict
import asyncio

from models.task import Task, TaskSendParams, TaskQueryParams, TaskStatus, TaskState, Message
from models.request import SendTaskRequest, SendTaskResponse, GetTaskRequest, GetTaskResponse

class SymptomTaskManager:
    """
    Handles symptom-related tasks using a SymptomCheckerAgent.
    """

    def __init__(self, orchestrator_agent):
        self.orchestrator = orchestrator_agent
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
        user_input = params.message.parts[0].text

        task = await self.upsert_task(params)

        try:
            response_text = await self.orchestrator.invoke(user_input, session_id=params.sessionId)
        except Exception as e:
            response_text = f"Error: {e}"

        agent_message = Message(
            role="agent",
            parts=[{"type": "text", "text": response_text}]
        )

        async with self.lock:
            task.history.append(agent_message)
            task.status.state = TaskState.COMPLETED

        return SendTaskResponse(id=request.id, result=task)

    async def on_get_task(self, request: GetTaskRequest) -> GetTaskResponse:
        query = request.params
        async with self.lock:
            task = self.tasks.get(query.id)
            if not task:
                return GetTaskResponse(id=request.id, error={"message": "Task not found"})

            task_copy = task.model_copy()
            if query.historyLength is not None:
                task_copy.history = task_copy.history[-query.historyLength:]

            return GetTaskResponse(id=request.id, result=task_copy)
