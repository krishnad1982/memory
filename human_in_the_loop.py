import asyncio

from agent_framework import (
    WorkflowContext,
    Executor,
    handler,
    response_handler,
    WorkflowBuilder,
)


class TravelExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="travel_executor")

    @handler
    async def handle(self, request: dict, ctx: WorkflowContext[dict]):
        origin = request["origin"]
        destination = request["destination"]

        travel = {
            "origin": origin,
            "destination": destination,
        }

        await ctx.send_message(travel)


class FlightExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="flight_executor")

    @handler
    async def handle(self, travel: dict, ctx: WorkflowContext[dict]):
        travel["flight_number"] = "QF421"

        await ctx.send_message(travel)


class HumanApprovalExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="human_approval_executor")

    @handler
    async def request_approval(
        self,
        travel: dict,
        ctx: WorkflowContext[dict],
    ):
        print("\nRequesting human approval...")

        await ctx.request_info(
            request_data={
                "type": "travel_approval",
                "travel": travel,
                "message": "Approve this travel request?",
            },
            response_type=str,
        )

    @response_handler
    async def handle_approval_response(
        self,
        original_request: dict,
        response: str,
        ctx: WorkflowContext[dict],
    ):
        travel = original_request["travel"]

        if response.lower() == "approve":
            travel["approved"] = True
            await ctx.send_message(travel)

        else:
            travel["approved"] = False
            travel["status"] = "rejected"

            await ctx.yield_output(travel)


class ResultExecutor(Executor):
    def __init__(self) -> None:
        super().__init__(id="result_executor")

    @handler
    async def handle(
        self,
        travel: dict,
        ctx: WorkflowContext[None, dict],
    ):
        travel["status"] = "completed"

        await ctx.yield_output(travel)


async def main():

    travel_executor = TravelExecutor()
    flight_executor = FlightExecutor()
    human_approval_executor = HumanApprovalExecutor()
    result_executor = ResultExecutor()

    builder = WorkflowBuilder(
        name="travel_workflow",
        start_executor=travel_executor,
    )
    builder.add_edge(
        travel_executor,
        flight_executor,
    )
    builder.add_edge(
        flight_executor,
        human_approval_executor,
    )
    builder.add_edge(
        human_approval_executor,
        result_executor,
    )
    workflow = builder.build()

    request = {
        "origin": "Sydney",
        "destination": "Melbourne",
    }

    result = await workflow.run(
        message=request,
    )
    approval_requests = result.get_request_info_events()

    if not approval_requests:
        print("No approval request received")
        return

    responses = {}

    for event in approval_requests:

        print("\n========================")
        print("HUMAN APPROVAL REQUIRED")
        print("========================")

        print(event.data)

        human_response = input("\nApprove travel? (approve/reject): ")

        responses[event.request_id] = human_response

    result = await workflow.run(
        responses=responses,
    )

    for output in result.get_outputs():
        print("\nFINAL OUTPUT:")
        print(output)


if __name__ == "__main__":
    asyncio.run(main())
