# Temporary test repository

## Navigation
- [PRD](./PRD.md)
- [README](./README.md)
- [Agent instructions](./.github/copilot-instructions.md)
- [Contributor guide](./CONTRIBUTIONS.md)
- [Roadmap](./ROADMAP.md)

## Overview
This repository is being onboarded for a new Django product that provides a website and DRF API for viewing and managing network infrastructure.

The system models:
- sites (datacentres)
- devices (routers and switches) at each site
- interfaces on each device
- existing connections between devices

Planned access model:
- **Network engineers**: view + manage
- **Customers**: view only

User and permission administration for now will be handled by superusers through Django admin.

UI approach is TBD between a ready-made theme and a Bootstrap-based custom UI.

## Overall high-level design of the app
TODO: add high-level architecture and component design.

## Assumptions and limitations
TODO: document assumptions and known limits.

- Temporary proof-of-concept limitation: change permissions are granted only to superusers at this stage.
- The repository now includes a proof-of-concept migration that creates `admin` / `admin123` for local testing only (strictly prohibited for real-world deployment).
- Note: deployment architecture implementation (async Django via ASGI, a Gunicorn service running multiple Uvicorn workers—typically about 2x available CPU cores—fronted by Nginx reverse proxy) is intentionally out of scope for this onboarding phase.
- Temporary proof-of-concept limitation: current CI test setup installs dependencies and applies migrations on every run. In a production-grade setup, CI should instead use a pre-built container image with dependencies pre-installed and migrations pre-applied, maintained by a separate workflow that rebuilds the image when requirements or migrations change.
- Temporary proof-of-concept limitation: `src/requirements.txt` intentionally tracks unfrozen/latest dependency versions for this toy repository; production-grade setups should pin and regularly review exact versions.
- Temporary proof-of-concept limitation: there is currently only one settings environment. A production-grade setup should use separate settings for local development, CI, production (and optionally staging), selected by an environment variable from `.env`.
- Temporary proof-of-concept limitation: tests intentionally have no explanatory comments because the current test cases are simple enough to be self-explanatory. In a production-grade test suite, each test should explain what it does and why.
- Temporary proof-of-concept limitation: in the Docker setup, the application and database run on the same machine and in the same container, which is "good enough for now".

## REST API

The application exposes a full REST API built with Django REST Framework (DRF).

### Interactive documentation (browser)

Once the application is running, the following interactive UIs are available without any additional tooling:

| URL | Description |
|-----|-------------|
| `/api/schema/swagger/` | Swagger UI — try requests directly from the browser |
| `/api/schema/redoc/` | ReDoc — clean reference documentation |
| `/api/schema/` | Raw OpenAPI schema download (JSON/YAML) |

### Endpoints

| Prefix | Description |
|--------|-------------|
| `GET /api/v1/sites/` | List all sites |
| `GET /api/v1/devices/` | List all devices |
| `GET /api/v1/interfaces/` | List all interfaces |
| `GET /api/v1/connections/` | List all connections |
| `GET /api/v1/connections/traced/?type=<site\|device\|interface>&id=<pk>` | List all connections touching a given object |

Standard CRUD (POST, GET `{id}/`, PUT/PATCH `{id}/`, DELETE `{id}/`) is available on all four model prefixes.  List endpoints return paginated results (100 items per page).

### Authentication

The API uses Django session authentication.  Log in via the Django admin (`/admin/`) or the standard login form to obtain a session cookie.  All endpoints (including read-only) require authentication; unauthenticated requests receive a `403 Forbidden` response.

Write operations (POST, PUT, PATCH, DELETE) are restricted to superusers.

### A note on docstrings

DRF-Spectacular automatically includes ViewSet and serializer docstrings in the generated OpenAPI schema and renders them in Swagger UI and ReDoc.  Any text in a docstring is therefore **user-facing documentation** and should be written accordingly.

## How to set up, install and run

### Docker requirements
- Docker must be installed and available on your host machine.

### Run with Docker - Option 1
1. Build the image locally from this repository:
   ```bash
   docker build -t tmp_aa:local .
   ```
2. Run the container:
   ```bash
   docker run --rm -p 8000:8000 tmp_aa:local
   ```

This builds everything from scratch and is therefore terribly slow.

### Run with Docker - Option 2
We considered distributing a pre-baked local image archive from this repository, but it required an enormous download split across several files, so it was not practical and was abandoned.

Notes:
- This approach would have created a maintenance headache: the baked image archive would need to be rebuilt and refreshed with future developments.
- We also considered publishing the image via `ghcr.io`, but in this PoC stage it was not deemed practical because the user received an `access denied` error.

### Run without Docker - Option 3 (not practical - too demanding to the tester)
This is how a tester can run the app similarly to the author setup, but it pre-supposes the tester already has PostgreSQL on the host and can create a new user with database-creation permissions.

1. Create and activate a local virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```
3. Create a PostgreSQL user and database on the host (example):
   ```bash
   createuser --pwprompt --createdb aa_user
   createdb -O aa_user aa_db
   ```
4. Export DB settings to point Django to that host PostgreSQL instance:
   ```bash
   export POSTGRES_HOST=127.0.0.1
   export POSTGRES_PORT=5432
   export POSTGRES_DB=aa_db
   export POSTGRES_TEST_DB=aa_test_db
   export POSTGRES_USER=aa_user
   export POSTGRES_PASSWORD=your_password
   ```
5. Run migrations and start Django:
   ```bash
   python src/manage.py migrate --noinput
   python src/manage.py runserver 0.0.0.0:8000
   ```

### Option 4 - TODO
The demo site will be hosted elsewhere and linked from this document.

Then open `http://127.0.0.1:8000/` in your browser on the host machine (outside the container).

### Temporary superuser creation (CLI)
The proof-of-concept migration creates `admin/admin123` automatically.
