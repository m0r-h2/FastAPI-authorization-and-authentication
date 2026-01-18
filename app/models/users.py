from sqlalchemy import (
    Integer, String, Text, Boolean, DateTime
)

from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="Уникальный идентификатор пользователя")
    first_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="Имя пользователя")
    last_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="Фамилия пользователя")
    middle_name: Mapped[str] = mapped_column(String(50), nullable=False, comment="Отчество пользователя")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False, comment="Email пользователя")
    password_hash: Mapped[str] = mapped_column(Text, nullable=False, comment="Хэш пароля")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="Активен ли пользователь")
    role: Mapped[str] = mapped_column(String, default="user", comment="Роль пользователя")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now,  comment="Дата и время создания пользователя")
