from pydantic import BaseModel, EmailStr


class LoginData(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    password: str
    confirm_password: str
