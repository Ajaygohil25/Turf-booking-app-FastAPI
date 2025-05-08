from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.base_declarative_model import BaseDeclarativeModel


class Roles(Base, BaseDeclarativeModel):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    role_name = Column(String, nullable=False)
    # relationships
    users = relationship("User", back_populates = "role")