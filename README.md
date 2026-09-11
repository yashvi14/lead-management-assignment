# Lead Management Application

A take-home implementation for creating, viewing, and updating prospect leads.

## Features

- Public lead intake form
- Required fields: first name, last name, email, resume/CV
- Resume upload validation
- Persistent lead storage
- Email acknowledgment to prospect
- Email notification to attorney
- Attorney login
- Protected internal leads dashboard
- Lead state workflow: `PENDING` → `REACHED_OUT`
- Protected resume download
- FastAPI backend
- Next.js frontend
- Production-style service/repository separation
- Basic backend tests

## Architecture

```text
Browser
  |
  +--> Next.js public form ------------------+
  |                                          |
  +--> Next.js internal dashboard            |
                                             v
                                      FastAPI REST API
                                       /          \
                                      /            \
                              SQLAlchemy/SQLite   File Storage
                                      |
                                  Lead records

FastAPI --> EmailService --> Resend API
                         \-> console fallback for local dev
```

For more detail, see [DESIGN.md](./DESIGN.md).

---

## 1. Prerequisites

Install:

- Python 3.11+
- Node.js 20+
- npm

The project is designed to run directly from VS Code with two terminals.

---

## 2. Run the backend

Open a terminal:

```bash
cd backend
python -m venv .venv
```

Activate it:

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

Windows:

```powershell
copy .env.example .env
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

Backend URLs:

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Default local attorney credentials

The `.env.example` file contains:

```text
ADMIN_EMAIL=attorney@example.com
ADMIN_PASSWORD=change-me
```

These are intentionally environment-driven rather than stored in source code/database.

---

## 3. Run the frontend

Open a second terminal:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Windows:

```powershell
copy .env.local.example .env.local
npm run dev
```

Open:

- Public form: http://localhost:3000
- Attorney login: http://localhost:3000/admin/login
- Attorney dashboard: http://localhost:3000/admin

---

## 4. Email integration

The backend supports Resend.

To enable real email delivery, configure:

```text
RESEND_API_KEY=re_xxx
EMAIL_FROM=Leads <onboarding@your-verified-domain.com>
ATTORNEY_EMAIL=attorney@company.com
```

If `RESEND_API_KEY` is empty, the application logs the email payload to the backend console. This makes the entire workflow testable locally without requiring a third-party account.

Email delivery runs after lead persistence as a FastAPI background task. A temporary email-provider failure therefore does not cause a submitted lead to be lost.

---

## 5. Run tests

From `backend/`:

```bash
pytest
```

---

## 6. API summary

### Public

```http
POST /api/v1/leads
Content-Type: multipart/form-data
```

Fields:

- `first_name`
- `last_name`
- `email`
- `resume`

### Auth

```http
POST /api/v1/auth/login
```

```json
{
  "email": "attorney@example.com",
  "password": "change-me"
}
```

### Internal

All internal endpoints require:

```http
Authorization: Bearer <token>
```

Endpoints:

```http
GET   /api/v1/leads
GET   /api/v1/leads/{lead_id}/resume
PATCH /api/v1/leads/{lead_id}/status
```

Status request:

```json
{
  "status": "REACHED_OUT"
}
```

The API explicitly prevents moving a lead back from `REACHED_OUT` to `PENDING`.

---

## 7. Suggested demo flow

For the screen recording:

1. Open `/`.
2. Fill the public lead form and attach a PDF.
3. Submit it and show the success state.
4. Show backend console email messages, or real emails if Resend is configured.
5. Open `/admin/login`.
6. Sign in with the attorney credentials.
7. Show the newly created lead.
8. Open/download the resume.
9. Click **Mark Reached Out**.
10. Show the state change from `PENDING` to `REACHED_OUT`.
11. Briefly show Swagger and the repository docs.

---

## 8. Repository documents

- `README.md` — setup/run instructions
- `DESIGN.md` — architecture and tradeoffs
- `AGENT_USAGE.md` — coding-agent usage write-up and prompt excerpts
- `NOTES.md` — attribution between agent-generated and manually reviewed code
