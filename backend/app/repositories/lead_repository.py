from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, lead: Lead) -> Lead:
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def list_all(self) -> list[Lead]:
        statement = select(Lead).order_by(Lead.created_at.desc())
        return list(self.db.scalars(statement).all())

    def get(self, lead_id: str) -> Lead | None:
        return self.db.get(Lead, lead_id)

    def save(self, lead: Lead) -> Lead:
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
