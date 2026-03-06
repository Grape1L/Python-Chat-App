from pydantic import BaseModel, EmailStr
from datetime import date

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    birthdate: date

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    # is_active: bool - later
    
class UsernameModel(BaseModel):
    username: str