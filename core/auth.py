from datetime import datetime, timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from models.user_model import UserModel
from pydantic import EmailStr
from pytz import timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from core.security import verify_password

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f'{settings.API_V1_STR}/user/login'
)


async def authenticate(
    email: EmailStr, password: str, db: AsyncSession
) -> Optional[UserModel]:
    async with db as session:
        query = select(UserModel).filter(UserModel.email == email)
        result = await session.execute(query)
        user: UserModel = result.scalars().unique().one_or_none()

        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        return user


def _create_token(type: str, time_life: timedelta, sub: str) -> str:
    payload = {}
    am = timezone('America/Manaus')
    now = datetime.now(tz=am)
    expires = now + time_life

    payload.update({
        'type': type,
        'exp': expires,
        'iat': now,
        'sub': str(sub)
    })

    return jwt.encode(
        payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM
    )


def create_token_acess(sub: str) -> str:
    return _create_token(
        type='acess_token',
        time_life=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub
    )
