from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.base_declarative_model import BaseDeclarativeModel

class ManageTurfManager(Base, BaseDeclarativeModel):
    __tablename__ = 'manage_turf_manager'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    turf_id = Column(UUID(as_uuid=True), ForeignKey("turf.id"), nullable=False)
    turf_manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # relationship
    turf = relationship("Turf",back_populates="turf_managers")
    users = relationship("User", back_populates="turf_managers")