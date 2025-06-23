import logging
import click

from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.appointment_agent.task_manager import AppointmentTaskManager
from agents.appointment_agent.agent import AppointmentAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

@click.command()
@click.option("--host", default="localhost", help="Host to bind AppointmentAgent server to")
@click.option("--port", default=10010, help="Port for AppointmentAgent server")
def main(host: str, port: int):
    print(f"\n🚑 Starting AppointmentAgent on http://{host}:{port}/\n")

    capabilities = AgentCapabilities(streaming=False)

    skill = AgentSkill(
        id="book_appointment",
        name="Doctor Appointment Scheduler",
        description="Schedules medical appointments based on patient symptoms and preferences",
        tags=["healthcare", "appointment", "doctor", "scheduler"],
        examples=[
            "Book a dentist appointment for tomorrow morning",
            "Schedule a cardiologist for chest pain symptoms",
            "I need to see an eye specialist next week"
        ]
    )

    agent_card = AgentCard(
        name="AppointmentAgent",
        description="Agent that schedules healthcare appointments based on symptoms and patient preferences.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[skill],
    )

    appointment_agent = AppointmentAgent()
    task_manager = AppointmentTaskManager(agent=appointment_agent)

    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=task_manager
    )
    server.start()

if _name_ == "_main_":
    main()