import uuid
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    _id:str = uuid.uuid4()
    user_name:str = Field(required = True)
    email:EmailStr = Field(required = True)
    password:str = Field(required = True)

