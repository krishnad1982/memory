import asyncio

from travel_model import TripState
from datetime import datetime
from zoneinfo import ZoneInfo

from agent_framework import (
    WorkflowContext,
    Executor,
    handler,
    WorkflowBuilder,
)


class TravelExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="trip_request")

    @handler
    async def handle(self, request: dict, ctx: WorkflowContext[str]):
        user_date = datetime.strptime(request["travel_date"], "%d-%m-%Y")
        zone_date = user_date.replace(tzinfo=ZoneInfo("Australia/Sydney"))
        trip_state = TripState(
            origin=request["origin"],
            destination=request["destination"],
            travel_date=zone_date,
        )
        ctx.set_state("trip_state", trip_state)
        await ctx.send_message("SEARCH_FLIGHT")


class FlightExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="flight_search")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[str]):
        trip_state: TripState = ctx.get_state("trip_state")
        trip_state.selected_flight = "QF421"
        trip_state.flight_price = 500.00
        ctx.set_state("trip_state", trip_state)
        await ctx.send_message("CHECK_POLICY")


class PolicyExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="policy_check")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[str]):
        trip_state: TripState = ctx.get_state("trip_state")
        if trip_state.flight_price is None:
            raise ValueError("Flight price must exist before policy check.")
        trip_state.policy_checked = True
        trip_state.policy_compliant = trip_state.flight_price <= 400
        ctx.set_state("trip_state", trip_state)
        await ctx.send_message("COMPLETE")


class ResultExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="complete")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[None, TripState]):
        trip_state: TripState = ctx.get_state("trip_state")
        await ctx.yield_output(trip_state)


async def main():
    travel_executor = TravelExecutor()
    flight_executor = FlightExecutor()
    policy_executor = PolicyExecutor()
    result_executor = ResultExecutor()

    builder = WorkflowBuilder(
        start_executor=travel_executor,
    )

    builder.add_edge(travel_executor, flight_executor)
    builder.add_edge(flight_executor, policy_executor)
    builder.add_edge(policy_executor, result_executor)
    workflow = builder.build()
    request = {
        "origin": "sydney",
        "destination": "melbourne",
        "travel_date": "15-10-2026",
    }
    async for event in workflow.run(message=request, stream=True):
        # print(event) enable this line to see the events in the workflow
        if event.type == "output":
            trip_state: TripState = event.data
            print("Final Trip State:")
            print(trip_state)


asyncio.run(main())
