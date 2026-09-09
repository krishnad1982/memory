import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

INTERACTION_FILE = Path("interaction_history.json")


def _load_history() -> dict:
    if INTERACTION_FILE.exists():
        with INTERACTION_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    return {}


def _save_history(history: dict) -> None:
    with INTERACTION_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            indent=2,
            default=str,
        )


def create_trip(
    trip_id: str,
    trip_details: dict[str, Any],
) -> None:
    history = _load_history()

    if trip_id in history:
        return

    history[trip_id] = {
        "trip": trip_details,
        "interactions": [],
    }

    _save_history(history)


def add_interaction(
    trip_id: str,
    event_type: str,
    details: dict[str, Any],
) -> None:
    history = _load_history()

    if trip_id not in history:
        raise ValueError(
            f"Trip '{trip_id}' does not exist. "
            "Call create_trip() before adding interactions."
        )

    interaction = {
        "timestamp": datetime.now(ZoneInfo("Australia/Sydney")).isoformat(),
        "event_type": event_type,
        "details": details,
    }

    history[trip_id]["interactions"].append(interaction)

    _save_history(history)


def get_trip_interactions(trip_id: str) -> dict | None:
    history = _load_history()
    return history.get(trip_id)


def find_trips_by_destination(destination: str) -> list[dict]:
    history = _load_history()

    matches = []

    for trip_id, record in history.items():
        trip = record.get("trip", {})

        if trip.get("destination", "").lower() == destination.lower():
            matches.append(
                {
                    "trip_id": trip_id,
                    **record,
                }
            )

    return matches
