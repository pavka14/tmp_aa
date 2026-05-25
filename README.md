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
- TODO: add a data migration that creates an `admin` user with password `admin123` for testing only (strictly prohibited for real-world deployment).
- Note: deployment architecture implementation (async Django via ASGI, a Gunicorn service running multiple Uvicorn workers—typically about 2x available CPU cores—fronted by Nginx reverse proxy) is intentionally out of scope for this onboarding phase.
- Temporary proof-of-concept limitation: current CI test setup installs dependencies and applies migrations on every run. In a production-grade setup, CI should instead use a pre-built container image with dependencies pre-installed and migrations pre-applied, maintained by a separate workflow that rebuilds the image when requirements or migrations change.
- Temporary proof-of-concept limitation: `src/requirements.txt` intentionally tracks unfrozen/latest dependency versions for this toy repository; production-grade setups should pin and regularly review exact versions.

## How to set up, install and run
TODO: add local setup, installation, and run instructions.

### Temporary superuser creation (CLI)
Use Django management command:

```bash
python manage.py createsuperuser
```
