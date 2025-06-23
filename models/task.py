# =============================================================================
# models/task.py
# =============================================================================
# Purpose:
# Task-related data models for a healthcare-focused Agent2Agent (A2A) system.
#
# Used across:
# - AppointmentAgent (e.g., booking follow-ups)
# - SymptomCheckerAgent (e.g., triaging conditions)
# - HealthRecordsAgent (e.g., retrieving EMRs)
# =============================================================================

from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Any, Literal, List
from datetime import datetime


# -----------------------------------------------------------------------------
# Message Part (text only, e.g., symptoms or instructions)
# -----------------------------------------------------------------------------
class TextPart(BaseModel):
    type: Literal["text"] = "text"
    text: str  # Example: "I have a persistent headache"

Part = TextPart  # For future extensibility (e.g., add image, JSON)


# -----------------------------------------------------------------------------
# Message: A single message from user or agent (used in task history)
# -----------------------------------------------------------------------------
class Message(BaseModel):
    role: Literal["user", "agent"]  # Sender of the message
    parts: List[Part]               # Currently only text parts


# -----------------------------------------------------------------------------
# TaskStatus: Tracks the lifecycle of a healthcare task
# -----------------------------------------------------------------------------
class TaskStatus(BaseModel):
    state: str
    timestamp: datetime = Field(default_factory=datetime.now)


# -----------------------------------------------------------------------------
# Task: Core object representing a healthcare query or command
# -----------------------------------------------------------------------------
class Task(BaseModel):
    id: str                          # Unique identifier per task
    status: TaskStatus               # Current state (submitted, working, etc.)
    history: List[Message]           # List of user-agent exchanges


# -----------------------------------------------------------------------------
# Request Parameter Models
# -----------------------------------------------------------------------------

# Base parameters to identify a task
class TaskIdParams(BaseModel):
    id: str
    metadata: dict[str, Any] | None = None


# Extended task query to control history
class TaskQueryParams(TaskIdParams):
    historyLength: int | None = None


# Payload to send a new task (used by agents and CLI)
class TaskSendParams(BaseModel):
    id: str
    sessionId: str = Field(default_factory=lambda: uuid4().hex)
    message: Message
    historyLength: int | None = None
    metadata: dict[str, Any] | None = None


# -----------------------------------------------------------------------------
# TaskState Enum: Lifecycle stages in a healthcare context
# -----------------------------------------------------------------------------
class TaskState(str, Enum):
    SUBMITTED = "submitted"           # Example: "Patient described chest pain"
    WORKING = "working"               # Agent is reasoning (e.g., LLM + tools)
    INPUT_REQUIRED = "input-required" # Example: Awaiting date/time from user
    COMPLETED = "completed"           # Appointment booked, symptom resolved
    CANCELED = "canceled"             # User or system aborted task
    FAILED = "failed"                 # Agent or system error
    UNKNOWN = "unknown"               # Fallback for invalid state
