import json

from agent_framework import tool
from interaction_memory import find_trips_by_destination


@tool(approval_mode="never_require")
def get_previous_trip(destination: str) -> str:
    """Retrieve previous trip interactions for a destination."""

    trips = find_trips_by_destination(destination)

    if not trips:
        return f"No previous trips found for {destination}."

    latest_trip = trips[-1]

    return json.dumps(
        latest_trip,
        indent=2,
        default=str,
    )
