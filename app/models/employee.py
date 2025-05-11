import uuid
from pydantic import BaseModel, Field, EmailStr

class Employee(BaseModel):
    employee_name: str = Field(required=True)
    email: EmailStr = Field(required=True)
    is_shift_manager: bool = Field(required=True, default=False)


