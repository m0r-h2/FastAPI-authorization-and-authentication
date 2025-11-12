from pydantic import BaseModel, Field, EmailStr, ConfigDict

from datetime import datetime


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=50, description="Имя пользователя")
    last_name: str = Field(..., max_length=50, description="Фамилия Пользователя")
    middle_name: str = Field(max_length=50, description="Отчество Пользователя (если есть)")
    email: EmailStr = Field(max_length=250, description="Email пользователя")
    password: str = Field(min_length=4, description="Пароль (минимум 4 символов)")
    verf_password: str = Field(min_length=4, description="Пароль (минимум 4 символов)")
    role: str = Field(default="user", pattern="^(user|admin)$", description="Роль: 'user' или 'admin'")


class UserUpdate(BaseModel):
    first_name: str = Field(..., max_length=50, description="Имя пользователя")
    last_name: str = Field(..., max_length=50, description="Фамилия Пользователя")
    middle_name: str = Field(max_length=50, description="Отчество Пользователя (если есть)")
    email: EmailStr = Field(max_length=250, description="Email пользователя")
    password_hash: str = Field(min_length=4, description="Пароль (минимум 4 символов)")


class UserUpdateAdmin(BaseModel):
    first_name: str = Field(..., max_length=50, description="Имя пользователя")
    last_name: str = Field(..., max_length=50, description="Фамилия Пользователя")
    middle_name: str = Field(max_length=50, description="Отчество Пользователя (если есть)")


class UserPassword(BaseModel):
    password: str = Field(min_length=4, description="Пароль (минимум 4 символов)")
