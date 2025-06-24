from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class AgentSkill(BaseModel):
    name: str
    description: Optional[str] = None


class AgentCapability(BaseModel):
    type: str  # e.g., "symptom_checking", "appointment_booking"
    skills: List[AgentSkill]


class AgentCapabilities(BaseModel):
    capabilities: List[AgentCapability]


class AgentCard(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    version: Optional[str] = "1.0"
    url: Optional[HttpUrl] = None
    capabilities: Optional[AgentCapabilities] = None
    tools: Optional[List[dict[str, str]]] = []
