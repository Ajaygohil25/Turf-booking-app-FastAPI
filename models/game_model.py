from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.base_declarative_model import BaseDeclarativeModel


class Game(Base,BaseDeclarativeModel):
    __tablename__ = 'game'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    game_name = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # relationship
    turfs = relationship("Turf", back_populates="game")