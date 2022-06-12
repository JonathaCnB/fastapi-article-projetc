from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from models.user_model import UserModel
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.auth import oauth2_schema
from core.config import settings
from core.database import Session


class TokenData(BaseModel):
    username: Optional[str] = None


async def get_session() -> AsyncGenerator:
    session: AsyncSession = Session()

    try:
        yield session
    finally:
        await session.close()


async def get_current_user(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_schema)
) -> UserModel:
    credential_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Não Autorizado',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )
        username: str = payload.get("sub")

        if username is None:
            raise credential_exception

        token_data: TokenData = TokenData(username=username)

    except JWTError:
        raise credential_exception

    async with db as session:
        query = select(UserModel).filter(
            UserModel.id == int(token_data.username)
        )
        result = await session.execute(query)
        user: UserModel = result.scalars().unique().one_or_none()

        if user is None:
            return credential_exception

        return user
