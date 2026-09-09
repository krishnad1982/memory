from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TripState:
    trip_id: str
    origin: str
    destination: str
    travel_date: datetime

    selected_flight: Optional[str] = None
    flight_price: Optional[float] = None

    policy_checked: bool = False
    policy_compliant: bool = False
