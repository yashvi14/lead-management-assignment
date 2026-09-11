from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.security import require_admin
from app.models.lead import LeadStatus
from app.schemas.lead import LeadCreateResponse, LeadResponse, LeadStatusUpdate
from app.services.email_service import EmailService
from app.services.lead_service import LeadService
from app.services.storage import LocalFileStorage

router = APIRouter(prefix="/leads", tags=["leads"])


def get_lead_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LeadService:
    storage = LocalFileStorage(settings.upload_dir, settings.max_upload_bytes)
    return LeadService(db, storage)


@router.post("", response_model=LeadCreateResponse, status_code=201)
async def create_lead(
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    service: LeadService = Depends(get_lead_service),
    settings: Settings = Depends(get_settings),
) -> LeadCreateResponse:
    lead = await service.create_lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume=resume,
    )

    email_service = EmailService(settings)
    background_tasks.add_task(email_service.send_lead_notifications, lead)

    return LeadCreateResponse(
        id=lead.id,
        status=lead.status,
        message="Lead submitted successfully",
    )


@router.get(
    "",
    response_model=list[LeadResponse],
    dependencies=[Depends(require_admin)],
)
def list_leads(
    service: LeadService = Depends(get_lead_service),
) -> list[LeadResponse]:
    return [LeadResponse.model_validate(lead) for lead in service.list_leads()]


@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse,
    dependencies=[Depends(require_admin)],
)
def update_lead_status(
    lead_id: str,
    body: LeadStatusUpdate,
    service: LeadService = Depends(get_lead_service),
) -> LeadResponse:
    lead = service.update_status(lead_id, body.status)
    return LeadResponse.model_validate(lead)


@router.get(
    "/{lead_id}/resume",
    dependencies=[Depends(require_admin)],
)
def download_resume(
    lead_id: str,
    service: LeadService = Depends(get_lead_service),
) -> FileResponse:
    lead = service.get_lead(lead_id)
    path: Path = service.storage.path_for(lead.resume_storage_name)

    if not path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resume file not found")

    return FileResponse(
        path,
        media_type=lead.resume_content_type,
        filename=lead.resume_original_name,
    )
