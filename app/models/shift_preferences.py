from enum import Enum
from typing import List
from pydantic import BaseModel

from models.employee import Employee
from models.time_models import ShiftDate

class ShiftType(Enum):
    day = "Day"
    night = "Night"
    standby = "Standby"


class Preference(BaseModel):
    start_date: ShiftDate
    shift_type: ShiftType
    availability: bool


class EmployeePreferences(BaseModel):
    employee_obj : Employee
    preferences : List[Preference]







    