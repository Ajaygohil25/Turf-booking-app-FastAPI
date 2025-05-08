from uuid import uuid4
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base


class BlackListToken(Base):
    __tablename__ = "blacklist_token"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    token = Column(String, nullable=False)
