from sqlalchemy import Column, String
from core.database import Base


class OtherEvent(Base):
    __tablename__ = "other_events"

    event_id = Column(String(255), primary_key=True)

    def __repr__(self):
        return f"<OtherEvent(event_id={self.event_id})>"
