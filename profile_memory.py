import json
from pathlib import Path
from typing import Any

PROFILE_FILE = Path("user_profiles.json")


def _load_profiles() -> dict:
    if PROFILE_FILE.exists():
        with PROFILE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    return {}


def _save_profiles(profiles: dict) -> None:
    with PROFILE_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            profiles,
            file,
            indent=2,
            default=str,
        )


def get_profile(user_id: str) -> dict:
    profiles = _load_profiles()

    return profiles.get(user_id, {})


def update_profile(
    user_id: str,
    key: str,
    value: Any,
) -> None:
    profiles = _load_profiles()

    if user_id not in profiles:
        profiles[user_id] = {}

    profiles[user_id][key] = value

    _save_profiles(profiles)
