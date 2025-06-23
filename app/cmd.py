# =============================================================================
# cmd.py (Healthcare Agent Client)
# =============================================================================
# Purpose:
# A CLI client for interacting with healthcare agents using the A2A protocol.
# It supports sending messages to agents (e.g., "Book an appointment",
# "Check symptoms", "Get my records") and viewing the responses.
# =============================================================================

import asyncclick as click
import asyncio
from uuid import uuid4

from client.client import A2AClient
from models.task import Task

@click.command()
@click.option("--agent", default="http://localhost:10010", help="Base URL of the healthcare agent server")
@click.option("--session", default=0, help="Session ID (use 0 to generate a new one)")
@click.option("--history", is_flag=True, help="Print full task history after receiving a response")

async def cli(agent: str, session: str, history: bool):
    """
    CLI for interacting with A2A healthcare agents.

    Args:
        agent (str): Base URL of the agent server (e.g., AppointmentAgent)
        session (str): Reuse or auto-generate a session ID
        history (bool): If true, print entire task history after response
    """
    client = A2AClient(url=agent)
    session_id = uuid4().hex if str(session) == "0" else str(session)

    while True:
        prompt = click.prompt("\n🩺 What would you like the healthcare agent to do? (type ':q' or 'quit' to exit)")

        if prompt.strip().lower() in [":q", "quit"]:
            print("👋 Exiting healthcare CLI...")
            break

        payload = {
            "id": uuid4().hex,
            "sessionId": session_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": prompt}]
            }
        }

        try:
            task: Task = await client.send_task(payload)

            if task.history and len(task.history) > 1:
                reply = task.history[-1]
                print("\n🤖 Agent response:", reply.parts[0].text)
            else:
                print("\n⚠️ No meaningful response received.")

            if history:
                print("\n🕓 Conversation History:")
                for msg in task.history:
                    print(f"[{msg.role}] {msg.parts[0].text}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(cli())
