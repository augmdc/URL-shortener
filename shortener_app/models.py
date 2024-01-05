# shortener_app/models.py

from sqlalchemy import Boolean, Column, Integer, String

from .database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    long_url = Column(String, index=True)
    short_url=Column(String, index=False)