from typing import List

from core.auth import authenticate, create_token_acess
from core.deps import get_current_user, get_session
from core.security import get_hash_password
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from models.user_model import UserModel
from schemas.user_schema import (UserSchemaArticle, UserSchemaBase,
                                 UserSchemaCreate, UserSchemaUpdate)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter()


@router.get(
    '/login',
    response_model=UserSchemaBase,
    status_code=status.HTTP_200_OK
)
def get_login(user: UserModel = Depends(get_current_user)):
    return user


@router.post('/login')
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session)
):
    user = await authenticate(
        email=form_data.username, password=form_data.password, db=db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Dados incorretos'
        )
    return JSONResponse(
        content={
            'acess_token': create_token_acess(sub=user.id),
            'token_type': 'bearer',
        },
        status_code=status.HTTP_200_OK
    )


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchemaBase
)
async def post_user(
    user: UserSchemaCreate,
    db: AsyncSession = Depends(get_session)
):
    new_user: UserModel = UserModel(
        name=user.name,
        last_name=user.last_name,
        email=user.email,
        password=get_hash_password(user.password),
        is_admin=user.is_admin
    )
    async with db as session:
        try:
            session.add(new_user)
            await session.commit()
            return new_user
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail='Dados inválidos'
            )


@router.get(
    '/',
    response_model=List[UserSchemaBase],
    status_code=status.HTTP_200_OK
)
async def get_users(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UserModel)
        result = await session.execute(query)
        users: List[UserSchemaBase] = result.scalars().unique().all()
        return users


@router.get(
    '/{user_id}',
    response_model=UserSchemaArticle,
    status_code=status.HTTP_200_OK
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_session)
):
    async with db as session:
        qs = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(qs)
        user: UserSchemaArticle = result.scalars().unique().one_or_none()
        if user:
            return user

        raise HTTPException(
            detail='Usuário não encontrado',
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.put(
    '/{user_id}',
    response_model=UserSchemaBase,
    status_code=status.HTTP_200_OK
)
async def put_user(
    user_id: int,
    user: UserSchemaUpdate,
    user_obj: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    async with db as session:
        if user_obj:
            qs = select(UserModel).filter(UserModel.id == user_id)
            result = await session.execute(qs)
            user_update: UserSchemaArticle = (
                result.scalars().unique().one_or_none()
            )
            if user_update:
                if user.name:
                    user_update.name = user.name
                if user.last_name:
                    user_update.last_name = user.last_name
                if user.email:
                    user_update.email = user.email
                if user.is_admin:
                    user_update.is_admin = user.is_admin
                if user.password:
                    user_update.password = get_hash_password(user.password)

                await session.commit()
                return user_update
        raise HTTPException(
            detail='Usuário não encontrado',
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(
    user_id: int,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    async with db as session:
        if user:
            qs = select(UserModel).filter(UserModel.id == user_id)
            result = await session.execute(qs)
            user_delete: UserSchemaArticle = (
                result.scalars().unique().one_or_none()
            )
            if user_delete:
                await session.delete(user_delete)
                await session.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail='Usuário não encontrado',
            status_code=status.HTTP_404_NOT_FOUND
        )
