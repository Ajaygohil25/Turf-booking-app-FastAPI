from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.base_declarative_model import BaseDeclarativeModel

class Revenue(Base, BaseDeclarativeModel):
    __tablename__ = 'revenue'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    turf_booking_id = Column(UUID(as_uuid=True), ForeignKey("turf_booking.id"), nullable=False)
    amount = Column(Integer, nullable=False)

    # relationship
    turf_booking = relationship("TurfBooking",back_populates="revenue")