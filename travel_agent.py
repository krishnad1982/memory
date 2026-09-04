import asyncio

from datetime import datetime
from agent_framework import Agent, tool
from core import get_chat_client
from travel_model import TripState

trip_state = TripState(origin="", destination="", travel_date=datetime.now())


# ---------------------------------------------------------
# 2. TOOLS
# ---------------------------------------------------------


@tool(approval_mode="never_require")
def set_trip(
    origin: str,
    destination: str,
    travel_date: str,
) -> str:
    """Set the trip currently being planned.

    travel_date must be supplied as YYYY-MM-DD.
    """

    trip_state.origin = origin
    trip_state.destination = destination
    trip_state.travel_date = datetime.fromisoformat(travel_date)

    return f"Trip set from {origin} to {destination} " f"on {travel_date}."


@tool(approval_mode="never_require")
def search_flights() -> str:
    """Find a flight for the current trip."""

    if not trip_state.origin or not trip_state.destination:
        return "Trip details are incomplete."

    # Fake flight search for our learning exercise
    trip_state.selected_flight = "QF421"
    trip_state.flight_price = 315.00

    return (
        f"Found QF421 from {trip_state.origin} "
        f"to {trip_state.destination} for $315."
    )


@tool(approval_mode="never_require")
def check_policy() -> str:
    """Check whether the currently selected flight complies with policy."""

    if trip_state.flight_price is None:
        return "No flight has been selected."

    trip_state.policy_checked = True
    trip_state.policy_compliant = trip_state.flight_price <= 400

    if trip_state.policy_compliant:
        return "The selected flight complies with travel policy."

    return "The selected flight does not comply with travel policy."


@tool(approval_mode="never_require")
def get_trip_state() -> str:
    """Return the current working-memory state."""

    return str(trip_state)


# ---------------------------------------------------------
# 3. AGENT
# ---------------------------------------------------------


async def main():
    agent = Agent(
        client=get_chat_client(),
        name="TravelMate",
        instructions="""
            You are a corporate travel assistant.
            Use the available tools to manage the trip.
            Rules:
            - When the user provides origin, destination and travel date,call set_trip.
            - When asked to find a flight, call search_flights.
            - When asked about policy compliance, call check_policy.
            - Do not invent trip or flight details.
            """,
        tools=[
            set_trip,
            search_flights,
            check_policy,
            get_trip_state,
        ],
    )

    print("Initial working memory:")
    print(trip_state)
    print()

    result = await agent.run(
        "I need to travel from Sydney to Melbourne on 2026-10-15.Then find a flight and check if it complies with policy."
    )

    print("Agent:")
    print(result)

    print("\nWorking memory after turn 1:")
    print(trip_state)


if __name__ == "__main__":
    asyncio.run(main())
