import secrets

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import Settings, get_settings
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    email_ok = secrets.compare_digest(body.email.lower(), settings.admin_email.lower())
    password_ok = secrets.compare_digest(body.password, settings.admin_password)

    if not (email_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    return TokenResponse(
        access_token=create_access_token(settings.admin_email, settings)
    )
