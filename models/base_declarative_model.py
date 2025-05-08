from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declared_attr

class BaseDeclarativeModel:
    @declared_attr
    def created_by(self):
        return Column(UUID(as_uuid=True), nullable=True)

    @declared_attr
    def updated_by(self):
        return Column(UUID(as_uuid=True), nullable=True)

    @declared_attr
    def created_at(self):
        return Column(DateTime, default=func.now(), nullable=True)

    @declared_attr
    def updated_at(self):
        return Column(DateTime, onupdate=func.now(), nullable=True)
