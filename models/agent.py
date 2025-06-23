from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict


class AgentCapability(BaseModel):
    name: str


class AgentSkill(BaseModel):
    name: str


class AgentCard(BaseModel):
    id: Optional[str]
    name: str
    description: Optional[str] = None
    version: Optional[str] = "1.0"
    url: Optional[HttpUrl] = None
    capabilities: Optional[List[AgentCapability]] = []
    skills: Optional[List[AgentSkill]] = []
    tools: Optional[List[Dict[str, str]]] = []
