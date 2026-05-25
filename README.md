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

## How to set up, install and run

### Docker requirements
- Docker must be installed and available on your host machine.

### Run with Docker
1. Build the image locally from this repository:
   ```bash
   docker build -t tmp_aa:local .
   ```
2. Run the container:
   ```bash
   docker run --rm -p 8000:8000 tmp_aa:local
   ```

Then open `http://127.0.0.1:8000/` in your browser on the host machine (outside the container).

### Temporary superuser creation (CLI)
The proof-of-concept migration creates `admin/admin123` automatically.
