from uuid import uuid4
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from core.database import Base
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from models.base_declarative_model import BaseDeclarativeModel


class Address(Base, BaseDeclarativeModel):
    __tablename__ = "address"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    street_address = Column(String, nullable=False)
    area = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey("city.id"))
    is_active = Column(Boolean, nullable=False)
    turf_owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    lat = Column(Float, nullable=False)
    long = Column(Float, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)

    # relationship
    turf = relationship("Turf", back_populates = "addresses")
    city = relationship("City", back_populates = "addresses")
    users = relationship("User", back_populates = "addresses")