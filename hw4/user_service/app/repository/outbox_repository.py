from typing import List
from sqlalchemy.orm import Session
from model.outbox import OutboxEvent

class OutboxRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, event: OutboxEvent) -> OutboxEvent:
        self.session.add(event)
        self.session.flush()
        # self.session.commit()
        # self.session.refresh(event)
        return event

    def get_pending(self) -> List[OutboxEvent]:
        return self.session.query(OutboxEvent).filter_by(pending=True).all()

    def get_all(self) -> List[OutboxEvent]:
        return self.session.query(OutboxEvent).all()

    def mark_as_published(self, event: OutboxEvent) -> None:
        event.pending = False
        self.session.commit()
