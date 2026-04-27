from sqlalchemy.orm import Session
from model.other_event import OtherEvent


class OtherEventRepository:
    def __init__(self, session: Session):
        self.session = session

    def exists(self, event_id: str) -> bool:
        return self.session.query(OtherEvent).filter_by(event_id=event_id).first() is not None

    def create(self, event_id: str) -> OtherEvent:
        if self.exists(event_id):
            raise ValueError(f"OtherEvent with id '{event_id}' already exists")

        event = OtherEvent(event_id=event_id)
        self.session.add(event)
        self.session.flush()
        # self.session.commit()
        # self.session.refresh(event)
        return event
