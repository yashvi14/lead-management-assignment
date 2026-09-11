# System Design

## 1. Requirements

The system has two surfaces.

### Public prospect flow

A prospect can submit:

- first name
- last name
- email
- resume/CV

After a successful submission:

1. The lead is persisted with status `PENDING`.
2. The uploaded resume is persisted.
3. The prospect receives a confirmation email.
4. An attorney receives a new-lead notification.

### Internal attorney flow

Authenticated attorneys can:

- view all leads
- inspect prospect information
- download the uploaded resume
- mark a `PENDING` lead as `REACHED_OUT`

---

## 2. High-level architecture

```text
                    +---------------------+
                    |      Prospect       |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |       Next.js       |
                    | public + admin UI   |
                    +----------+----------+
                               |
                               | HTTPS / REST
                               v
                    +---------------------+
                    |       FastAPI       |
                    | auth / validation   |
                    | business logic      |
                    +--+---------+------+-+
                       |         |      |
                       v         v      v
                 +--------+ +--------+ +-------------+
                 |   DB   | | Resume | | Email       |
                 | leads  | |Storage | | Provider    |
                 +--------+ +--------+ +-------------+
```

---

## 3. Data model

### Lead

| Field | Type | Notes |
|---|---|---|
| id | UUID/string | Primary key |
| first_name | string | Required |
| last_name | string | Required |
| email | string | Required |
| resume_original_name | string | Original filename |
| resume_storage_name | string | Generated safe filename |
| resume_content_type | string | Validated MIME type |
| status | enum | `PENDING` or `REACHED_OUT` |
| created_at | datetime | UTC |
| updated_at | datetime | UTC |

The stored filename is generated server-side. User-provided filenames are never used as filesystem paths.

---

## 4. API design

### `POST /api/v1/leads`

Public endpoint accepting multipart form data.

The server:

1. validates textual fields
2. validates extension/content type
3. enforces an upload-size limit
4. writes the resume through the storage abstraction
5. persists the lead
6. schedules notification emails

Returning the lead ID makes the endpoint observable and testable while avoiding exposure of internal-only fields.

### `GET /api/v1/leads`

JWT-protected endpoint used by the internal dashboard.

For a larger data set this endpoint would support cursor pagination, filters, search, and sorting. The take-home implementation returns recent leads ordered by creation time.

### `PATCH /api/v1/leads/{id}/status`

JWT-protected state transition endpoint.

Allowed transition:

```text
PENDING --> REACHED_OUT
```

The API rejects the reverse transition rather than relying on UI behavior.

### `GET /api/v1/leads/{id}/resume`

JWT-protected endpoint.

Resumes contain sensitive candidate data, so the file is not mounted as a public static directory.

---

## 5. Authentication

For the take-home, attorney credentials are stored as environment variables and successful login returns a short-lived signed JWT.

This keeps the implementation small while still enforcing server-side authorization.

For production I would replace this with the company's SSO/OIDC provider, store the session in a Secure + HttpOnly cookie, support RBAC, audit attorney actions, and remove static administrator credentials entirely.

---

## 6. Persistence choice

SQLite is used locally because it makes the assignment runnable with zero infrastructure.

The application accesses it through SQLAlchemy rather than raw SQL, keeping the domain/data-access boundary portable.

Production migration:

```text
SQLite --> PostgreSQL
```

would require primarily a configuration change plus schema migrations.

For production I would add Alembic rather than relying on `create_all()` at application start.

---

## 7. Resume storage

The implementation provides a `LocalFileStorage` service.

This is appropriate for the local exercise but deliberately isolated behind a service class.

Production migration:

```text
LocalFileStorage --> S3/GCS
```

Recommended production behavior:

- private bucket
- server-side encryption
- signed, expiring download URLs or authenticated proxy download
- antivirus/malware scanning
- file-size limits
- content sniffing
- lifecycle/retention policy

---

## 8. Email delivery

Email is delegated to an `EmailService`.

The implementation supports Resend and falls back to console output when no API key is present.

The lead is persisted before email delivery. This is deliberate: a transient external email outage should not make the company lose a prospect.

For higher reliability I would use an outbox/job queue:

```text
Lead transaction
    |
    +--> leads row
    +--> email_outbox row

Worker --> retries --> provider
```

This gives durable retries and observability.

---

## 9. Security

Implemented:

- server-side authentication for internal endpoints
- JWT expiry
- CORS allowlist
- upload size limit
- filename randomization
- file-type allowlist
- Pydantic validation
- protected resume retrieval
- state transition enforcement
- secrets through environment variables

Production additions:

- SSO/OIDC
- HttpOnly cookies instead of browser local storage
- CSRF defense where appropriate
- rate limiting on public submissions/login
- CAPTCHA/bot mitigation
- antivirus scan
- audit logs
- database encryption/backups
- secret manager
- structured logging/tracing
- stricter MIME/content validation

---

## 10. Reliability and scaling

The API layer is stateless except for local development file storage.

A production deployment can horizontally scale FastAPI and Next.js when:

- PostgreSQL is externalized
- resumes are moved to object storage
- email work is moved to a durable queue

Likely bottlenecks are storage and external email delivery, not the simple lead database queries.

---

## 11. Observability

For production I would add:

- request IDs
- structured logs
- lead-created and lead-updated metrics
- email delivery success/failure metrics
- latency/error dashboards
- alerting on elevated 5xx rates
- audit history for attorney status updates

---

## 12. Testing strategy

Included backend tests exercise:

- health check
- public lead creation
- authentication failure/success
- protected lead listing
- state transition to `REACHED_OUT`

Additional production tests would cover malformed files, provider failures, permissions, concurrency, large uploads, and E2E browser flows.
