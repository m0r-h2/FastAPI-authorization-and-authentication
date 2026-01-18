import asyncio
from passlib.context import CryptContext
from sqlalchemy import select

from app.database.database import async_engine, async_session_maker, Base
from app.database.users import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_data = [
    {"first_name": "Александр", "last_name": "Иванов", "middle_name": "Петрович", "email": "alex.ivanov@example.com", "password": "4821", "role": "admin", "is_active": True},
    {"first_name": "Мария", "last_name": "Смирнова", "middle_name": "Алексеевна", "email": "maria.smirnova@example.com", "password": "9053", "role": "admin", "is_active": True},
    {"first_name": "Дмитрий", "last_name": "Кузнецов", "middle_name": "Игоревич", "email": "dmitry.kuznetsov@example.com", "password": "1177", "role": "admin", "is_active": True},
    {"first_name": "Ольга", "last_name": "Попова", "middle_name": "Николаевна", "email": "olga.popova@example.com", "password": "3008", "role": "user", "is_active": False},
    {"first_name": "Игорь", "last_name": "Соколов", "middle_name": "Владимирович", "email": "igor.sokolov@example.com", "password": "7742", "role": "user", "is_active": False},
    {"first_name": "Елена", "last_name": "Лебедева", "middle_name": "Сергеевна", "email": "elena.lebedeva@example.com", "password": "6601", "role": "user", "is_active": False},
    {"first_name": "Виктор", "last_name": "Новиков", "middle_name": "Андреевич", "email": "viktor.novikov@example.com", "password": "2490", "role": "user", "is_active": True},
    {"first_name": "Наталья", "last_name": "Морозова", "middle_name": "Павловна", "email": "natalia.morozova@example.com", "password": "1338", "role": "user", "is_active": True},
    {"first_name": "Сергей", "last_name": "Соловьёв", "middle_name": "Михайлович", "email": "sergey.soloviev@example.com", "password": "5574", "role": "user", "is_active": True},
    {"first_name": "Анна", "last_name": "Васильева", "middle_name": "Юрьевна", "email": "anna.vasileva@example.com", "password": "4026", "role": "user", "is_active": True},
    {"first_name": "Павел", "last_name": "Григорьев", "middle_name": "Романович", "email": "pavel.grigorev@example.com", "password": "8899", "role": "user", "is_active": True},
    {"first_name": "Ксения", "last_name": "Михайлова", "middle_name": "Викторовна", "email": "kseniya.mikhailova@example.com", "password": "2165", "role": "user", "is_active": True},
    {"first_name": "Роман", "last_name": "Орлов", "middle_name": "Денисович", "email": "roman.orlov@example.com", "password": "0312", "role": "user", "is_active": True},
    {"first_name": "Людмила", "last_name": "Козлова", "middle_name": "Ивановна", "email": "lyudmila.kozlova@example.com", "password": "4757", "role": "user", "is_active": True},
    {"first_name": "Максим", "last_name": "Никитин", "middle_name": "Артемович", "email": "maksim.nikitin@example.com", "password": "9084", "role": "user", "is_active": True}
]

async def seed():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        result = await session.execute(select(User))
        if result.scalars().first():
            print("Users already exist — skipping seed.")
            return

        users = []
        for u in users_data:
            password_hash = pwd_context.hash(u["password"])
            users.append(User(
                first_name=u["first_name"],
                last_name=u["last_name"],
                middle_name=u["middle_name"],
                email=u["email"],
                password_hash=password_hash,
                is_active=u["is_active"],
                role=u["role"]
            ))

        session.add_all(users)
        await session.commit()
        print("Seed completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
