from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.base_declarative_model import BaseDeclarativeModel

class Media(Base, BaseDeclarativeModel):
    __tablename__ = 'media'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    turf_id = Column(UUID(as_uuid=True), ForeignKey("turf.id"), nullable=False)
    media_url = Column(String, nullable=False)

    # relationship
    turf = relationship("Turf",back_populates="media")