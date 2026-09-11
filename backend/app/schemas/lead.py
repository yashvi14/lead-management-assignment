from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.lead import LeadStatus


class LeadCreateResponse(BaseModel):
    id: str
    status: LeadStatus
    message: str


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    email: EmailStr
    resume_original_name: str
    resume_content_type: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime


class LeadStatusUpdate(BaseModel):
    status: LeadStatus
