from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_password

from app.database.crud import (
    get_user_by_email,
    create_user,
    authenticate_user,
    update_user,
    deactivate_user
)

from app.schemas.users import (
    User as UserResponse,
    UserCreate,
    UserUpdate,
    UserPassword
)

from app.database.users import User as UserModel
from app.database.db_depends import get_async_db

from app.auth import (
    create_access_token,
    get_current_user,
    create_refresh_token
)

import jwt

from app.config import SECRET_KEY, ALGORITHM


router = APIRouter(prefix="/users",
                   tags=["users"])



@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    if await get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email уже существует"
        )

    if user.password != user.verf_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пароли не совпадают"
        )

    return await create_user(db, user.model_dump())



@router.post("/refresh-token")
async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user_by_email(db, email)
    if not user:
        raise credentials_exception

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    user = await authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный Email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(
            data={"sub": user.email, "role": user.role, "id": user.id}
        ),
        "refresh_token": create_refresh_token(
            data={"sub": user.email, "role": user.role, "id": user.id}
        ),
        "token_type": "bearer",
    }



@router.put("/me")
async def update_account(
    data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    await update_user(
        db,
        current_user,
        data.model_dump(exclude_unset=True)
    )

    return {"message": "Вы успешно обновили свой аккаунт"}



@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_account(
    password: UserPassword,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    if not verify_password(password.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid password"
        )

    await deactivate_user(db, current_user.id)

    return {"message": "Аккаунт удален"}

