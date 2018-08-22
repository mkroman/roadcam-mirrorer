from sqlalchemy import Column, Integer, String, DateTime

from . import base


class Download(base.Base):
    __tablename__ = 'downloads'

    id = Column(Integer, primary_key=True)
    thing_id = Column(String)
    url = Column(String)
    title = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    downloaded_at = Column(DateTime)
    path = Column(String)
