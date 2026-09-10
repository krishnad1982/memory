import json

from agent_framework import tool, FunctionInvocationContext
from interaction_memory import find_trips_by_destination
from profile_memory import get_profile, update_profile


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


@tool(approval_mode="never_require")
def save_user_preference(
    user_id: str,
    preference_name: str,
    preference_value: str,
) -> str:
    """Save a durable travel preference for a user."""

    update_profile(
        user_id=user_id,
        key=preference_name,
        value=preference_value,
    )

    return f"Saved preference " f"{preference_name}={preference_value}"


@tool(approval_mode="never_require")
def get_user_profile(
    ctx: FunctionInvocationContext,
) -> str:
    """Retrieve the stored travel profile for a user."""
    session = ctx.session
    if session is None:
        return "No active session."
    profile = get_profile(session.state.get("user_id", ""))

    if not profile:
        return "No stored profile exists for this user."

    return json.dumps(
        profile,
        indent=2,
        default=str,
    )
