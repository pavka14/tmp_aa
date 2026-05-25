# tmp_aa

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

Note: deployment architecture implementation (async Django via ASGI, Uvicorn service with multiple Gunicorn workers, Nginx reverse proxy) is intentionally out of scope for this onboarding phase.

## How to set up, install and run
TODO: add local setup, installation, and run instructions.
