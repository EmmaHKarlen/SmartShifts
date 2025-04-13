from pydantic import BaseModel, Field, validator


class Time(BaseModel):
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