from core.config import settings
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class ArticleModel(settings.BDBaseModel):
    __tablename__ = 'aticles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(String(255))
    url_font = Column(String(255))
    user_id = Column(Integer, ForeignKey('users.id'))
    creator = relationship(
        'UserModel', back_populates='articles', lazy='joined'
    )
