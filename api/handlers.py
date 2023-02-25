from logging import getLogger
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.actions.user import _create_new_user, _delete_user, _activate_user, _get_user_by_id, _get_user_by_email, \
    _update_user
from api.models import UserCreate, ShowUser, DeleteUserResponse, ActivateUserResponse, UpdatedUserResponse, \
    UpdateUserRequest
from db.dals import UserDAL
from db.session import get_db

logger = getLogger(__name__)

user_router = APIRouter()


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.delete('/', response_model=DeleteUserResponse)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
    deleted_user_id = await _delete_user(user_id=user_id, session=db)
    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.put('/', response_model=ActivateUserResponse)
async def activate_user(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ActivateUserResponse:
    activated_user_id = await _activate_user(user_id=user_id, session=db)
    if activated_user_id is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return ActivateUserResponse(activated_user_id=activated_user_id)


@user_router.get('/', response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_id(user_id=user_id, session=db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    return user


@user_router.get('/email/', response_model=ShowUser)
async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_email(email=email, session=db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with email {email} not found."
        )
    return user


@user_router.patch('/', response_model=UpdatedUserResponse)
async def update_user_by_id(user_id: UUID, body: UpdateUserRequest,
                            db: AsyncSession = Depends(get_db)) -> UpdatedUserResponse:
    updated_user_params = body.dict(exclude_none=True)
    if updated_user_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )
    user = await _get_user_by_id(user_id=user_id, session=db)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )
    try:
        updated_user_id = await _update_user(updated_user_params=updated_user_params, session=db, user_id=user_id)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")
    return UpdatedUserResponse(updated_user_id=updated_user_id)
