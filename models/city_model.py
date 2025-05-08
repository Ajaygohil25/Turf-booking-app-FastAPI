from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from core.database import Base

class City(Base):
    __tablename__ = "city"
    id = Column(Integer, primary_key=True,autoincrement=True)
    city_name = Column(String, nullable=False)
    state_id = Column(Integer, ForeignKey("state.id"))

    # relationship
    state = relationship("State", back_populates="city")
    addresses = relationship("Address", back_populates="city")
    users = relationship("User", back_populates="city")




