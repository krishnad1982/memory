from dataclasses import dataclass, field
from datetime import datetime, timezone
from agent_framework import Agent
from core import get_chat_client


@dataclass
class WorkerMemoryState:
    task_id: str
    request_text: str
    extracted_requirements: list[str] = field(default_factory=list)
    candidate_options: list[str] = field(default_factory=list)
    current_step: str = "not started"

    def clear(self):
        self.extracted_requirements.clear()
        self.candidate_options.clear()
        self.current_step = "cleared"


class ArchitectureReviewAgent:
    def __init__(self) -> None:
        self._agent = Agent(
            client=get_chat_client(),
            name="RequirementsExtractor",
            instructions="""You extract functional and non-functional requirements from an
                architecture request. Respond with a short bullet list only — 
                no preamble, no explanation.""",
        )
        self._active_states: dict[str, WorkerMemoryState] = {}

    def start_task(self, task_id: str, request_text: str) -> WorkerMemoryState:
        current_state = WorkerMemoryState(task_id=task_id, request_text=request_text)
        self._active_states[task_id] = current_state
        return current_state

    async def extract_requirements(self, task_id: str) -> WorkerMemoryState:
        current_state = self._active_states.get(task_id)
        if current_state is None:
            raise ValueError(f"Task {task_id} not found")
        assistant_result = await self._agent.run(current_state.request_text)
        current_state.extracted_requirements = [
            line.strip("- ").strip()
            for line in assistant_result.text.splitlines()
            if line.strip()
        ]
        current_state.current_step = "requirement extracted"
        return current_state

    def finish_task(self, task_id: str) -> WorkerMemoryState:
        current_state = self._active_states.pop(task_id)
        return current_state


import asyncio


async def test():
    agent = ArchitectureReviewAgent()
    task_id = "task-001"
    agent.start_task(
        task_id=task_id,
        request_text="We need a claims-processing API that integrates with Dataverse and handles 5000 concurrent users.",
    )
    state = await agent.extract_requirements(task_id=task_id)
    print(state.extracted_requirements)
    print(state.current_step)
    finish_state = agent.finish_task(task_id=task_id)
    print(agent._active_states.get(task_id))


asyncio.run(test())
