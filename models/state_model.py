from uuid import uuid4

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from core.database import Base
# from fastapi_utils.UUID_type import UUID, UUID_SERVER_DEFAULT_POSTGRESQL
from sqlalchemy.dialects.postgresql import UUID

class State(Base):
    __tablename__ = "state"
    id = Column(Integer, primary_key=True,autoincrement=True)
    state_name = Column(String, nullable=False)

    #relationship
    city = relationship("City", back_populates = "state")

