from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.base_declarative_model import BaseDeclarativeModel

class Discount(Base, BaseDeclarativeModel):
    __tablename__ = 'discount'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    turf_id = Column(UUID(as_uuid=True), ForeignKey("turf.id"), nullable=False)
    discount_amount = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Explicitly specifying foreign_keys
    turf = relationship("Turf", back_populates="discounts", foreign_keys=[turf_id])
