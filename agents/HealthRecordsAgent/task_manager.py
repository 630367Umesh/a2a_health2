# agents/health_records_agent/task_manager.py

from models.task import TaskRequest, TaskResponse
from agents.health_records_agent.agent import health_records_agent
from crewai import Crew, Task


class HealthRecordsTaskManager:
    def __init__(self, agent=health_records_agent):
        self.agent = agent

    async def handle_task(self, task_request: TaskRequest) -> TaskResponse:
        session_id = task_request.session_id or "default_session"
        query = task_request.input.text

        # Very basic parsing logic (can be improved with NLP)
        if "add note" in query.lower() or "update" in query.lower():
            # Expected format: "Add note to 101: Patient is improving"
            try:
                parts = query.split(":")
                id_part = parts[0].split()[-1]
                note = parts[1].strip()
                tasks = [
                    Task(
                        description=f"Add this note to patient ID {id_part}: {note}",
                        expected_output="A confirmation that the note was saved.",
                        agent=self.agent,
                    )
                ]
            except Exception as e:
                return TaskResponse(output={"text": f"Invalid input format: {str(e)}"})
        else:
            # Assume it's a fetch request
            id_part = ''.join(filter(str.isdigit, query))
            tasks = [
                Task(
                    description=f"Fetch the medical history for patient ID {id_part}.",
                    expected_output="A concise and accurate patient health summary.",
                    agent=self.agent,
                )
            ]

        crew = Crew(
            agents=[self.agent],
            tasks=tasks,
            verbose=False,
        )

        result = crew.run()
        return TaskResponse(output={"text": result})
