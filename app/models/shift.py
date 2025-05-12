import sys
from typing import List
import uuid
from pydantic import BaseModel, Field, validator
from models.time_models import ShiftDate, ShiftTime
from models.employee import Employee
sys.path.append('c:/Users/User/Desktop/smartShifts/SmartShifts/app')


class BaseShift(BaseModel):
    _id:str = Field(default_factory=lambda: str(uuid.uuid4()))
    employees_list: list[Employee] = Field(default=list())
    shift_manager: Employee = Field(required = True)
    standby_employee: Employee = Field(required=False, default=None)
    start_shift_date: ShiftDate
    end_shift_date: ShiftDate
    shift_start_time: ShiftTime
    shift_end_time: ShiftTime


class WeekDayShift(BaseShift):
    shift_start_time: ShiftTime = Field(default=ShiftTime(hour=8, minute=0))
    shift_end_time: ShiftTime = Field(default=ShiftTime(hour=17, minute=30))
    num_of_employees: int = 3


    def num_required_employees(self):
        return self.num_of_employees
    

    def is_required_standby_employee(self):
        return False
    

class WeekDayNightShift(BaseShift):
    shift_start_time: ShiftTime = Field(default=ShiftTime(hour=17, minute=0))
    shift_end_time: ShiftTime = Field(default=ShiftTime(hour=8, minute=30))
    num_of_employees: int = 2
    standby_employee: Employee = Field(required=True)


    def num_required_employees(self):
        return self.num_of_employees
    

    def is_required_standby_employee(self):
        return True
    

class WeekendShift(BaseShift):
    shift_start_time: ShiftTime = Field(default=ShiftTime(hour=9, minute=0))
    shift_end_time: ShiftTime = Field(default=ShiftTime(hour=9, minute=30))
    num_of_employees: int = 2
    standby_employee: Employee = Field(required=True)


    def num_required_employees(self):
        return self.num_of_employees
    
    
    def is_required_standby_employee(self):
        return True


class CreateShiftRequest(BaseModel):
    month: int
        

class CreateShiftResponse(BaseModel):
    shifts: List[BaseShift]
    link: str

