from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import (
    User as UserResponse,
    UserPassword,
    UserUpdateAdmin
)
from app.database.users import User as UserModel
from app.database.db_depends import get_async_db
from app.auth import get_current_role_admin, verify_password

from app.database.crud import (
    get_active_users,
    get_deleted_users,
    update_user_by_id,
    deactivate_user_by_id,
    get_user_by_id
)


router = APIRouter(
    prefix="/admins",
    tags=["admins"]
)


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_active_users(
    current_admin: UserModel = Depends(get_current_role_admin),
    db: AsyncSession = Depends(get_async_db)
):
    users = await get_active_users(db)
    return list(users)



@router.get(
    "/deleted",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_deleted_users(
    current_admin: UserModel = Depends(get_current_role_admin),
    db: AsyncSession = Depends(get_async_db)
):
    return await get_deleted_users(db)



@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdateAdmin,
    current_admin: UserModel = Depends(get_current_role_admin),
    db: AsyncSession = Depends(get_async_db)
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    await update_user_by_id(
        db,
        user_id,
        data.model_dump(exclude_unset=True)
    )

    return {"message": "Изменения сохранены"}



@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK
)
async def delete_user(
    user_id: int,
    password: UserPassword,
    current_admin: UserModel = Depends(get_current_role_admin),
    db: AsyncSession = Depends(get_async_db)
):
    if not verify_password(password.password, current_admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный пароль"
        )

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аккаунт либо удален, либо не существует"
        )

    await deactivate_user_by_id(db, user_id)

    return {"message": "Аккаунт удален"}

