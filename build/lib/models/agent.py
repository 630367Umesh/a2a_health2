# =============================================================================
# models/agent.py (Healthcare Use Case)
# =============================================================================
# Purpose:
# Pydantic models for describing healthcare agents in an A2A multi-agent system.
# These models are used for agent discovery, interaction, and capability declarations.
# =============================================================================

from pydantic import BaseModel
from typing import List


# -----------------------------------------------------------------------------
# AgentCapabilities: Describes what an agent supports (streaming, history, etc.)
# -----------------------------------------------------------------------------
class AgentCapabilities(BaseModel):
    streaming: bool = False                      # Can the agent stream responses?
    pushNotifications: bool = False              # Can it push updates to other agents?
    stateTransitionHistory: bool = False         # Does it record internal task state changes?


# -----------------------------------------------------------------------------
# AgentSkill: Describes one skill offered by a healthcare agent
# -----------------------------------------------------------------------------
class AgentSkill(BaseModel):
    id: str                                      # Unique skill ID (e.g., "check_symptoms")
    name: str                                    # Human-readable name
    description: str | None = None               # What the skill does
    tags: List[str] | None = None                # For search/discovery (e.g., ["appointment", "cardiology"])
    examples: List[str] | None = None            # Sample queries (e.g., "Book a doctor")
    inputModes: List[str] | None = None          # Input formats accepted (e.g., ["text"])
    outputModes: List[str] | None = None         # Output formats produced (e.g., ["text"])


# -----------------------------------------------------------------------------
# AgentCard: Describes a full healthcare agent and its capabilities
# -----------------------------------------------------------------------------
class AgentCard(BaseModel):
    name: str                                    # Agent name (e.g., "AppointmentAgent")
    description: str                             # Brief purpose (e.g., "Schedules appointments for patients")
    url: str                                     # Full base URL (e.g., http://localhost:10010)
    version: str                                 # Semantic version (e.g., "1.0.0")
    capabilities: AgentCapabilities              # Streaming/support features
    skills: List[AgentSkill]                     # The list of skills the agent supports
