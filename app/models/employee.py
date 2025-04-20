import uuid
from pydantic import BaseModel, Field, EmailStr

class Employee(BaseModel):
    _id:str = uuid.uuid4()
    employee_name:str = Field(required=True)
    email:EmailStr = Field(required=True)
    is_shift_manager = Field(required=True, default=False)


