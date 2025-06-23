# =============================================================================
# models/request.py
# =============================================================================
# Purpose:
# This module defines structured request models used in the A2A (Agent2Agent) protocol
# for your healthcare multi-agent system.
#
# These requests are used by:
# - SymptomCheckerAgent to initiate or route tasks
# - AppointmentAgent to book consultations
# - HealthRecordsAgent to retrieve patient history
#
# The models support:
# - Task submission ("tasks/send")
# - Task retrieval ("tasks/get")
#
# =============================================================================

from typing import Annotated, Union, Literal
from pydantic import Field
from pydantic.type_adapter import TypeAdapter

# Base JSON-RPC types
from models.json_rpc import JSONRPCRequest, JSONRPCResponse

# Task input/output models
from models.task import Task, TaskSendParams, TaskQueryParams


# -----------------------------------------------------------------------------
# SendTaskRequest
# -----------------------------------------------------------------------------
# Used by healthcare agents to submit a task.
# Example: SymptomCheckerAgent sends "chest pain" info to AppointmentAgent.
class SendTaskRequest(JSONRPCRequest):
    method: Literal["tasks/send"] = "tasks/send"
    params: TaskSendParams


# -----------------------------------------------------------------------------
# GetTaskRequest
# -----------------------------------------------------------------------------
# Used to retrieve task history or status.
# Example: HealthRecordsAgent retrieves past diagnosis for a session ID.
class GetTaskRequest(JSONRPCRequest):
    method: Literal["tasks/get"] = "tasks/get"
    params: TaskQueryParams


# -----------------------------------------------------------------------------
# A2ARequest: Unified request parser (based on the `method` field)
# -----------------------------------------------------------------------------
# Supports both sending and retrieving tasks across agents.
A2ARequest = TypeAdapter(
    Annotated[
        Union[
            SendTaskRequest,
            GetTaskRequest,
            # In future: CancelTaskRequest
        ],
        Field(discriminator="method")
    ]
)


# -----------------------------------------------------------------------------
# SendTaskResponse
# -----------------------------------------------------------------------------
# Returned when a healthcare agent successfully processes a task.
class SendTaskResponse(JSONRPCResponse):
    result: Task | None = None


# -----------------------------------------------------------------------------
# GetTaskResponse
# -----------------------------------------------------------------------------
# Returned when a task is queried — includes full task details and history.
class GetTaskResponse(JSONRPCResponse):
    result: Task | None = None
