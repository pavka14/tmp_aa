# ROADMAP

## Stage 1 — Repository onboarding and product definition
- [x] Add Product Requirements Document (PRD) with roles, entities, channels, and scope.
- [x] Add README with product overview and placeholder sections for design/assumptions/setup.
- [x] Add deployment-options notes and selected async deployment direction (planning only).
- [x] Add agent instructions for Python/Django/DRF and testing best practices.
- [x] Add CONTRIBUTIONS.md with lightweight contributor expectations and test-level definitions.

## Stage 2 — Project scaffolding
- [x] Initialize Django project and base app structure.
- [x] Add initial test setup and CI test command wiring.

## Stage 3 — Core data model
- [x] Implement `Site` model and admin configuration.
- [x] Implement `Device` model (router/switch type) linked to `Site`.
- [x] Implement `Interface` model linked to `Device`.
- [x] Implement `Connection` model linking interfaces/devices.
- [x] Add and review migrations for all core models.
- [x] Add proof-of-concept-only data migration for test admin user `admin` / `admin123` (never for real-world deployment).

## Stage 4 — Website implementation (static templates)
- [x] Add web interface with static views for homepage, docs, and API pages.
- [x] Add Bootstrap-based base layout with navigation, active-link state, and admin shortcut.
- [x] Add static homepage cards and modal hierarchy for sites, devices, interfaces, and connections.
- [x] Add placeholder Documentation and API Specifications pages.
- [x] Add tests covering static pages and static asset loading.
- [x] Add static assets required by the Django template pages.

## Stage 5 — API implementation (DRF)
- [x] Add Django REST Framework and baseline API configuration.
- [x] Add serializers for Site, Device, Interface, Connection.
- [x] Implement CRUD API endpoints with serializer-backed validation and error handling.
- [x] Handle CRUD failure cases (e.g., referential-integrity violations and permission denial).
- [x] Add API URL routing for DRF endpoints.
- [x] Add API tests for list/detail/create/update/delete and permissions.
- [x] Add `IsSuperUser` permission class (write restricted to superusers; documented as demo-grade in PRD).
- [x] Add site-name validators in `SiteSerializer` (min 4 / max 40); documented as proof-of-concept in PRD.
- [x] Add `connections/traced/` endpoint (by site, device, or interface) with nested response schema.
- [x] Install and configure DRF-Spectacular; add Swagger UI and ReDoc interactive schema browsers.
- [x] Update `/api/` static page with human-readable explanation, usage instructions, and links to interactive docs.
- [x] Update PRD with DRF, Spectacular, auth, permission, and validator design notes and limitations.

## Stage 6 — Website implementation (Django templates, dynamic data)
- [x] wire dynamic data to homepage
- [x] update documentation

## Stage 7 — Quality and operability (future)
- [ ] Configure environment-based settings split (dev/test/prod-ready structure).
- [ ] Add linting/formatting/static checks and documented local commands.
- [ ] Add structured logging and error-handling conventions.
- [ ] Add seed/sample data for local/demo use.
- [ ] Expand test coverage for edge cases and permissions.
- [ ] Document architecture and operational assumptions.

## Stage 8 — Packaging and runnable environments (future)
- [ ] Write complete installation and run instructions in README.
- [ ] Add Dockerfile for local runnable service.
- [ ] Add docker-compose setup for app + dependencies.
- [ ] Add one-command tester workflow to run and access UI in browser.
- [ ] Document API usage examples and smoke-test steps.

## Stage 9 — Deployment implementation (future)
- [ ] Implement ASGI deployment with Django in async-capable mode.
- [ ] Configure Gunicorn service running multiple Uvicorn workers (typically about 2x CPU cores).
- [ ] Add Nginx reverse proxy configuration.
- [ ] Add production deployment docs and rollout checklist.
- [ ] Add operational monitoring and health checks.
