# backend/sa_adapter/teacher_agent.py

from superior_agents.agent.base import BaseAgent
from superior_agents.agent.memory import AgentMemory
from backend.ai_analyzer import analyze_news_article  # adjust import if needed

class TeacherAgent(BaseAgent):
    def __init__(self, name="FudSniffAgent"):
        super().__init__(name=name)
        self.memory = AgentMemory(name)

    def think(self, input_data: str):
        # 1 - Store input to memory
        self.memory.store({"input": input_data})

        # 2 - Analyze sentiment via existing ai_analyzer logic
        signal = analyze_news_article(input_data)

        # 3 - Store output to memory
        self.memory.store({"output": signal})

        # 4 - Return signal
        return signal

    def recall_history(self):
        return self.memory.load_all()
