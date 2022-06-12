from fastapi import APIRouter

from api.v1.endpoints import article, user

api_router = APIRouter()
api_router.include_router(article.router, prefix='/articles', tags=['Artigos'])
api_router.include_router(user.router, prefix='/users', tags=['Usuários'])
