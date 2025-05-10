from enum import Enum
from typing import List
from pydantic import BaseModel

from app.models.time_models import ShiftDate

class ShiftType(Enum):
    day = "day"
    night = "night"
    standby = "standby"


class ShiftAvailability(Enum):
    unavailable = 0
    available = 1
    prefer = 2


class Preference(BaseModel):
    start_date: ShiftDate
    shift_type: ShiftType
    availability: ShiftAvailability


class EmployeePreferences(BaseModel):
    employee_id = str
    preferences = List[Preference]






    