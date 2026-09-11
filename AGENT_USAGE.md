# Coding-Agent Usage

## Short write-up

I used an AI coding assistant as an implementation partner for the take-home. I delegated repetitive scaffolding, initial FastAPI route/service structure, Next.js component boilerplate, test skeletons, and documentation outlines. I kept ownership of the architecture, API contract, data model, security boundaries, state transition rules, and final code review because those choices materially affect correctness and maintainability.

I also used the agent to challenge design decisions rather than only generate code. In particular, I asked it to identify failure modes around resume uploads and email delivery, then reviewed its suggestions against the assignment requirements.

One issue in the generated test setup involved SQLite database cleanup. The initial pytest fixture deleted the test database file while SQLAlchemy could still have pooled connections to it, which caused subsequent tests to fail with a readonly database error. I identified the issue by running the full test suite and reviewing the traceback, then fixed the fixture by resetting the schema and disposing SQLAlchemy connections correctly. After the change, all backend tests passed.

I manually reviewed generated code, ran the application locally, exercised the complete prospect-to-attorney workflow, and adjusted implementation details where needed.

## Representative prompt excerpts

### Prompt 1 — architecture

> Design a small production-style lead management application. The public side submits first name, last name, email and resume. FastAPI must provide the API and Next.js the web UI. Attorneys need an authenticated dashboard. Leads begin PENDING and can move to REACHED_OUT. Keep local setup simple but describe how each component would evolve in production.

### Prompt 2 — backend

> Create a FastAPI backend with clear separation between API routes, models, schemas, repositories/services, auth, storage and email integration. Use SQLAlchemy and SQLite locally. The lead creation endpoint must accept multipart form data and validate resume uploads.

### Prompt 3 — security review

> Review this lead-management implementation as if it handled real candidate data. Identify privacy/security issues involving resume storage, authentication, file paths, upload limits, status transitions, secrets and CORS. Suggest the smallest fixes appropriate for a take-home.

### Prompt 4 — frontend

> Implement a Next.js App Router UI with a polished public lead form and a simple protected attorney dashboard. Keep API interaction isolated in a small client module. Provide loading, error and success states.

### Prompt 5 — tests

> Add focused backend tests for lead creation, admin authentication, protected listing and the PENDING -> REACHED_OUT transition. Avoid testing implementation details.

## Verification performed manually

- Read generated routes and service code
- Verified internal routes require authentication
- Verified resume files are not exposed by a static directory
- Verified API enforces the status transition
- Verified submitted lead persists before notification email work
- Verified upload validation and size limits
- Ran backend tests
- Walked through public submission and attorney dashboard locally

### Example of catching and fixing an agent-generated issue

The initial generated pytest fixture deleted the SQLite test database file
while SQLAlchemy could still have pooled connections to it. This caused
subsequent tests to fail with `sqlite3.OperationalError: attempt to write a
readonly database`.

I identified the failure by running the full backend test suite and reviewing
the traceback. I fixed the fixture by resetting the schema with
`drop_all/create_all` and disposing SQLAlchemy connections instead of deleting
the active SQLite file. After the change, all 4 backend tests passed.
