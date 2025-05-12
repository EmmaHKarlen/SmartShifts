from pydantic import BaseModel, Field, validator


class ShiftTime(BaseModel):
    hour:int
    minute:int

    @validator("hour")
    @classmethod
    def hour_validator(cls, value):
        if value < 0 or value >= 25:
            raise ValueError("Date must be valid")
        return value
    
    @validator("minute")
    @classmethod
    def minute_validator(cls, value):
        if value < 0 or value >= 60:
            raise ValueError("Date must be valid")
        return value
    

class ShiftDate(BaseModel):
    day:int 
    month:int
    year:int

    @validator("day")
    @classmethod
    def day_validator(cls, value):
        if value <= 0 or value > 31:
            raise ValueError(f"Day must be valid, not: {value}")
        return value
    
    @validator("month")
    @classmethod
    def month_validator(cls, value):
        if value <= 0 or value >= 12:
            raise ValueError(f"Month must be valid, not: {value}")
        return value

    @validator("year")
    @classmethod
    def year_validator(cls, value):
        if value <= 2024 or value >= 2026:
            raise ValueError(f"Year must be valid, not: {value}")
        return value