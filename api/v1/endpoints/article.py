from typing import List

from core.deps import get_current_user, get_session
from fastapi import APIRouter, Depends, HTTPException, Response, status
from models.article_model import ArticleModel
from models.user_model import UserModel
from schemas.article_schema import ArticleSchema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter()


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=ArticleSchema
)
async def post_article(
    article: ArticleSchema,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    new_article: ArticleModel = ArticleModel(
        title=article.title,
        description=article.description,
        url_font=article.url_font,
        user_id=user.id
    )
    db.add(new_article)
    await db.commit()

    return new_article


@router.get(
    '/',
    response_model=List[ArticleSchema],
    status_code=status.HTTP_200_OK
)
async def get_articles(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(ArticleModel)
        result = await session.execute(query)
        articles: List[ArticleModel] = result.scalars().unique().all()
        return articles


@router.get(
    '/{article_id}',
    response_model=ArticleSchema,
    status_code=status.HTTP_200_OK
)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_session)
):
    async with db as session:
        query = select(ArticleModel).filter(ArticleModel.id == article_id)
        result = await session.execute(query)
        article: ArticleModel = result.scalars().unique().one_or_none()
        if article:
            return article
        raise HTTPException(
            detail='Artigo não encontrado',
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.put(
    '/{article_id}',
    response_model=ArticleSchema,
    status_code=status.HTTP_200_OK
)
async def put_article(
    article_id: int,
    article: ArticleSchema,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    async with db as session:
        query = select(ArticleModel).filter(ArticleModel.id == article_id)
        result = await session.execute(query)
        article_update: ArticleModel = result.scalars().unique().one_or_none()
        if article_update:
            if article.title:
                article_update.title = article.title
            if article.description:
                article_update.description = article.description
            if article.url_font:
                article_update.url_font = article.url_font
            if article.url_font:
                article_update.url_font = article.url_font
            if user.id != article_update.user_id:
                article_update.user_id = user.id

            return article_update
        raise HTTPException(
            detail='Artigo não encontrado',
            status_code=status.HTTP_404_NOT_FOUND
        )


@router.delete(
    '/{article_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_session),
    user: UserModel = Depends(get_current_user),
):
    async with db as session:
        query = select(ArticleModel).filter(ArticleModel.id == article_id)
        query = query.filter(ArticleModel.user_id == user.id)
        result = await session.execute(query)
        article: ArticleModel = result.scalars().unique().one_or_none()
        if article:
            await session.delete(article)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(
            detail='Artigo não encontrado',
            status_code=status.HTTP_404_NOT_FOUND
        )
