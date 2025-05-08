from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID

from models.admin_revenue_model import AdminRevenue
from models.base_declarative_model import BaseDeclarativeModel
from models.discount_model import Discount
from models.manage_turf_manager_model import ManageTurfManager


class Turf(Base, BaseDeclarativeModel):
    __tablename__ = "turf"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    turf_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amenities = Column(ARRAY(String))
    booking_price = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_verified = Column(Boolean, nullable=False)

    turf_owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    game_id = Column(UUID(as_uuid=True), ForeignKey("game.id"))
    address_id = Column(UUID(as_uuid=True), ForeignKey("address.id"))

    # relationships
    game = relationship("Game", back_populates="turfs")
    turf_owner = relationship("User", back_populates="turf")
    media = relationship("Media", back_populates="turf")
    discounts = relationship("Discount", back_populates="turf", foreign_keys=[Discount.turf_id])  # Ensure correct foreign_keys usage
    addresses = relationship("Address", back_populates="turf")
    admin_revenues_type = relationship("AdminRevenue", back_populates="turf", foreign_keys=[AdminRevenue.turf_id])
    turf_booking = relationship("TurfBooking", back_populates="turf")
    turf_managers = relationship("ManageTurfManager", back_populates="turf", foreign_keys=[ManageTurfManager.turf_id])
