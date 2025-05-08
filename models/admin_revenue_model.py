from uuid import uuid4
from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from core.database import Base
from models.base_declarative_model import BaseDeclarativeModel


class AdminRevenue(Base, BaseDeclarativeModel):
    __tablename__ = 'admin_revenue_mode'
    id = Column(UUID, primary_key=True, default=uuid4)
    turf_id = Column(UUID(as_uuid=True), ForeignKey("turf.id"), nullable=False)
    revenue_mode = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    Column(DateTime, default=func.now(), nullable=False)

    # relationship
    turf = relationship("Turf",back_populates="admin_revenues_type", foreign_keys=[turf_id])