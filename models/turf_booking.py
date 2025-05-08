from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.base_declarative_model import BaseDeclarativeModel

class TurfBooking(Base, BaseDeclarativeModel):
    __tablename__ = 'turf_booking'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    reservation_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_amount = Column(Integer, nullable=False)
    payment_status = Column(String, nullable=False)
    booking_status = Column(String, nullable=False)
    cancelled_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    cancel_reason = Column(String, nullable=True)

    turf_id = Column(UUID(as_uuid=True), ForeignKey('turf.id'))
    customer_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))

    # relationships
    turf = relationship('Turf', back_populates='turf_booking')

    customer = relationship('User', back_populates='turf_booking', foreign_keys=[customer_id])

    canceller = relationship('User', foreign_keys=[cancelled_by], back_populates='canceled_bookings')

    revenue = relationship('Revenue', back_populates='turf_booking')
    feedback = relationship('Feedback', back_populates='turf_booking')
