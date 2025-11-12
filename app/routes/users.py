from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.schemas.users import User as UserResponse, UserCreate, UserUpdate, UserPassword
from app.models.users import User as UserModel
from app.db_depends import get_async_db
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users",
                   tags=["users"])


@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_active_users(db: AsyncSession = Depends(get_async_db)):
    stmt = await db.scalars(select(UserModel).where(UserModel.is_active == True))
    return stmt


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")
    if user.password != user.verf_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="пароли не совпадают")

    db_user = UserModel(
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username, UserModel.is_active == True))
    user = result.first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/me")
async def update_account(
        data: UserUpdate,
        current_user: UserModel = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    update_data = data.model_dump(exclude_unset=True)

    update_data["password_hash"] = hash_password(data.password_hash)

    await db.execute(
        update(UserModel)
        .where(UserModel.id == current_user.id)
        .values(**update_data)
    )
    await db.commit()

    await db.refresh(current_user)

    return {"message": "Your data has been updated successfully."}


@router.delete("/", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_me_account(password: UserPassword,
                            current_user: UserModel = Depends(get_current_user),
                            db: AsyncSession = Depends(get_async_db)):
    if not verify_password(password.password, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")

    await db.execute(
        update(UserModel)
        .where(UserModel.id == current_user.id)
        .values(is_active=False)
    )
    await db.commit()
    return {"message": "Аккаунт удален"}
