from agents.host_agent.orchestrator import OrchestratorAgent
import asyncio

agent = OrchestratorAgent()
asyncio.run(agent.start())
