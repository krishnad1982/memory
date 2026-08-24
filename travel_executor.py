from travel_model import TripState
from datetime import datetime
from zoneinfo import ZoneInfo

from agent_framework import Workflow, WorkflowContext, Executor, handler


class TripRequestExecutor(Executor):
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


class FlightSearchExecutor(Executor):
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
        if not trip_state.policy_compliant:
            trip_state.approval_required = True
            trip_state.approval_status = "pending"
        ctx.set_state("trip_state", trip_state)
        await ctx.send_message("COMPLETE")


class CompleteExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="complete")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext[None, TripState]):
        trip_state: TripState = ctx.get_state("trip_state")
        await ctx.yield_output(trip_state)
