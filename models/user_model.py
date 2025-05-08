from uuid import uuid4
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from models.base_declarative_model import BaseDeclarativeModel

class User(Base, BaseDeclarativeModel):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    contact_no = Column(BigInteger, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    is_verified = Column(Boolean, nullable=False)

    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    city_id = Column(Integer, ForeignKey("city.id"))

    # relationships
    city = relationship("City", back_populates="users")
    role = relationship("Roles", back_populates = "users")
    turf = relationship("Turf", back_populates = "turf_owner")
    feedback = relationship("Feedback", back_populates = "customer")
    turf_managers = relationship("ManageTurfManager", back_populates = "users")
    addresses = relationship("Address", back_populates = "users")

    turf_booking = relationship(
        "TurfBooking",
        back_populates="customer",
        foreign_keys="[TurfBooking.customer_id]",
    )

    canceled_bookings = relationship(
        "TurfBooking",
        foreign_keys="[TurfBooking.cancelled_by]",
        back_populates="canceller",
    )