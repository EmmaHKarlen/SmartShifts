from pydantic import BaseModel, Field, validator

from app.models.time import Time
from app.models.user import User



class BaseShift(BaseModel):
    shift_manager:User = Field(required = True)
    day:int 
    month:int
    year:int
    shift_start_time:Time

    @validator("day")
    @classmethod
    def day_validator(cls, value):
        if value <= 0 or value >= 31:
            raise ValueError("Date must be valid")
        return value
    
    @validator("month")
    @classmethod
    def month_validator(cls, value):
        if value <= 0 or value >= 12:
            raise ValueError("Date must be valid")
        return value

    @validator("year")
    @classmethod
    def year_validator(cls, value):
        if value <= 2024 or value >= 2026:
            raise ValueError("Date must be valid")
        return value
    
morning_shift = BaseShift(shift_manager=User(user_name="emma199", email="emma2199@gmail.com", password="1234"), 
                          day = 21, month = 2, year = 2025, shift_start_time= Time(20, 0))

print(morning_shift)