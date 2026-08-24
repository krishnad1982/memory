import asyncio

from core import get_chat_client
from datetime import datetime
from agent_framework import (
    Agent,
    WorkflowBuilder,
    InMemoryCheckpointStorage,
)
from azure.identity import DefaultAzureCredential
from travel_executor import (
    TripRequestExecutor,
    FlightSearchExecutor,
    PolicyExecutor,
    CompleteExecutor,
)

travel_agent = Agent(
    client=get_chat_client(),
    name="TravelAgent",
    instructions="""
    You are a corporate travel assistant.
    Help users understand and plan business travel.
    Do not make up flight prices or booking information.
    """,
)


async def main():
    checkpoint_storage = InMemoryCheckpointStorage()

    trip_request_executor = TripRequestExecutor()
    flight_search_executor = FlightSearchExecutor()
    policy_executor = PolicyExecutor()
    complete_executor = CompleteExecutor()
    builder = WorkflowBuilder(
        name="travel_flow",
        start_executor=trip_request_executor,
        checkpoint_storage=checkpoint_storage,
    )
    builder.add_edge(trip_request_executor, flight_search_executor)
    builder.add_edge(flight_search_executor, policy_executor)
    builder.add_edge(policy_executor, complete_executor)

    workflow = builder.build()
    request = {
        "origin": "Sydney",
        "destination": "Melbourne",
        "travel_date": "25-08-2026",
    }

    async for event in workflow.run(message=request, stream=True):
        if event.type == "output":
            print(f"  FINAL OUTPUT: {event.data}")
        checkpoints = await checkpoint_storage.list_checkpoints(
            workflow_name="travel_flow"
        )
        # for checkpoint in checkpoints:
        #     print(checkpoint.checkpoint_id)


if __name__ == "__main__":
    asyncio.run(main())
