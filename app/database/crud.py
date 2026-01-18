from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database.users import User
from app.auth import hash_password, verify_password

from collections.abc import Sequence


async def get_active_users(db: AsyncSession) -> Sequence[User]:
    result = await db.scalars(
        select(User).where(User.is_active == True)
    )
    return result.all()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.scalars(
        select(User).where(User.email == email, User.is_active == True)
    )
    return result.first()


async def create_user(db: AsyncSession, data: dict) -> User:
    user = User(
        **data,
        password_hash=hash_password(data["password"])
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> User | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def update_user(
    db: AsyncSession,
    user: User,
    data: dict
):
    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))

    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(**data)
    )
    await db.commit()


async def deactivate_user(db: AsyncSession, user_id: int):
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False)
    )
    await db.commit()


async def get_deleted_users(db: AsyncSession):
    result = await db.scalars(
        select(User).where(User.is_active == False)
    )
    return result.all()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.scalars(
        select(User).where(User.id == user_id)
    )
    return result.first()


async def update_user_by_id(db: AsyncSession, user_id: int, data: dict):
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**data)
    )
    await db.commit()


async def deactivate_user_by_id(db: AsyncSession, user_id: int):
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False)
    )
    await db.commit()


