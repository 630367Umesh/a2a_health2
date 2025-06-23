class SymptomCheckerTaskManager:
    def __init__(self, agent):
        self.agent = agent

    async def handle_task(self, input_text: str, session_id: str) -> str:
        return self.agent.run(input_text)
