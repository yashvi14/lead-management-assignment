import logging

import httpx

from app.core.config import Settings
from app.models.lead import Lead

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def _send(self, to: str, subject: str, html: str) -> None:
        if not self.settings.resend_api_key:
            logger.warning(
                "EMAIL FALLBACK | to=%s | subject=%s | html=%s",
                to,
                subject,
                html,
            )
            return

        headers = {
            "Authorization": f"Bearer {self.settings.resend_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": self.settings.email_from,
            "to": [to],
            "subject": subject,
            "html": html,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

    async def send_lead_notifications(self, lead: Lead) -> None:
        try:
            await self._send(
                lead.email,
                "We received your information",
                (
                    f"<p>Hi {lead.first_name},</p>"
                    "<p>Thank you for reaching out. We received your information "
                    "and a member of our team will contact you soon.</p>"
                ),
            )
        except Exception:
            logger.exception("Could not send prospect email for lead %s", lead.id)

        try:
            await self._send(
                self.settings.attorney_email,
                f"New lead: {lead.first_name} {lead.last_name}",
                (
                    "<p>A new prospect submitted the lead form.</p>"
                    f"<p><strong>Name:</strong> {lead.first_name} {lead.last_name}<br/>"
                    f"<strong>Email:</strong> {lead.email}<br/>"
                    f"<strong>Lead ID:</strong> {lead.id}</p>"
                    "<p>Open the internal dashboard to review the resume.</p>"
                ),
            )
        except Exception:
            logger.exception("Could not send attorney email for lead %s", lead.id)
