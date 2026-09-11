from fastapi import HTTPException, UploadFile, status
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.orm import Session

from app.models.lead import Lead, LeadStatus
from app.repositories.lead_repository import LeadRepository
from app.services.storage import LocalFileStorage


class LeadService:
    def __init__(self, db: Session, storage: LocalFileStorage):
        self.repo = LeadRepository(db)
        self.storage = storage

    async def create_lead(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        resume: UploadFile,
    ) -> Lead:
        first_name = first_name.strip()
        last_name = last_name.strip()

        if not first_name or len(first_name) > 100:
            raise HTTPException(status_code=400, detail="Invalid first name")
        if not last_name or len(last_name) > 100:
            raise HTTPException(status_code=400, detail="Invalid last name")

        try:
            validated_email = str(TypeAdapter(EmailStr).validate_python(email.strip()))
        except ValidationError as exc:
            raise HTTPException(status_code=400, detail="Invalid email") from exc

        original_name, storage_name, content_type = await self.storage.save_resume(resume)

        lead = Lead(
            first_name=first_name,
            last_name=last_name,
            email=validated_email,
            resume_original_name=original_name,
            resume_storage_name=storage_name,
            resume_content_type=content_type,
            status=LeadStatus.PENDING,
        )

        try:
            return self.repo.create(lead)
        except Exception:
            # Avoid orphan files if DB persistence fails.
            self.storage.delete(storage_name)
            raise

    def list_leads(self) -> list[Lead]:
        return self.repo.list_all()

    def get_lead(self, lead_id: str) -> Lead:
        lead = self.repo.get(lead_id)
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found",
            )
        return lead

    def update_status(self, lead_id: str, new_status: LeadStatus) -> Lead:
        lead = self.get_lead(lead_id)

        if lead.status == new_status:
            return lead

        if lead.status == LeadStatus.PENDING and new_status == LeadStatus.REACHED_OUT:
            lead.status = new_status
            return self.repo.save(lead)

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid transition: {lead.status.value} -> {new_status.value}",
        )
