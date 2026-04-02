from core.database import Base
from sqlalchemy import Column, String, Boolean

class OutboxEvent(Base):
    __tablename__ = "outbox"

    data = Column(String(255), nullable=False)
    event_id = Column(String(255), primary_key=True)
    event_type = Column(String(255), nullable=False)
    pending = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<OutboxEvent(event_id={self.event_id}, pending={self.pending})>"
