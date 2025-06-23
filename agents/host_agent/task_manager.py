import logging
from models.json_rpc import JSONRPCResponse, InternalError

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, discovery):
        self.discovery = discovery

    async def on_send_task(self, task_request):
        logger.info(f"🔀 TaskManager received task: {task_request}")
        try:
            # Example logic to just echo task
            result = {
                "status": "routed",
                "task": task_request.task
            }
            return JSONRPCResponse(id=task_request.id, result=result)
        except Exception as e:
            return JSONRPCResponse(id=task_request.id, error=InternalError(message=str(e)))
