# =============================================================================
# models/json_rpc.py
# =============================================================================
# Purpose:
# This file defines the base classes and structures for JSON-RPC 2.0 messaging,
# adapted for a healthcare-focused multi-agent system using A2A protocol.
#
# These models standardize how agents like AppointmentAgent, SymptomCheckerAgent,
# and HealthRecordsAgent send and receive structured requests/responses.
# =============================================================================

from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# JSONRPCMessage (base class for requests/responses)
# -----------------------------------------------------------------------------
# All A2A-compliant healthcare agents use this format for consistent messaging.
class JSONRPCMessage(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str | None = Field(default_factory=lambda: uuid4().hex)

# -----------------------------------------------------------------------------
# JSONRPCRequest
# -----------------------------------------------------------------------------
# Used by one healthcare agent to call a method on another, such as:
# - SymptomCheckerAgent → AppointmentAgent
# - AppointmentAgent → HealthRecordsAgent
class JSONRPCRequest(JSONRPCMessage):
    method: str
    params: dict[str, Any] | None = None

# -----------------------------------------------------------------------------
# JSONRPCError
# -----------------------------------------------------------------------------
# Provides a structured error model used in failed A2A communications.
class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Any | None = None

# -----------------------------------------------------------------------------
# JSONRPCResponse
# -----------------------------------------------------------------------------
# Response to a JSON-RPC request, used in agent-to-agent replies.
class JSONRPCResponse(JSONRPCMessage):
    result: Any | None = None
    error: JSONRPCError | None = None

# -----------------------------------------------------------------------------
# InternalError
# -----------------------------------------------------------------------------
# Standard error returned when an agent encounters an unhandled exception.
class InternalError(JSONRPCError):
    code: int = -32603
    message: str = "Internal error"
    data: Any | None = None
