import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LeadStatus(str, enum.Enum):
    PENDING = "PENDING"
    REACHED_OUT = "REACHED_OUT"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)

    resume_original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    resume_storage_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    resume_content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus),
        nullable=False,
        default=LeadStatus.PENDING,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
