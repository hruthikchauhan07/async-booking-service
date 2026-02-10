from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


# -> input -> what we recieve from client

class UserCreate(BaseModel):
    email : EmailStr
    full_name : str
    password : str

# -> output -> what we show to the client

class UserResponce(BaseModel):
    id : int
    email : EmailStr
    full_name : str
    is_active : bool
    is_superuser : bool
    created_at : datetime

    #reads from ORM [object relation mapper]

    model_config = ConfigDict(from_attributes=True)

