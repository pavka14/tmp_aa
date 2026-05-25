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
- [ ] Implement `Site` model and admin configuration.
- [ ] Implement `Device` model (router/switch type) linked to `Site`.
- [ ] Implement `Interface` model linked to `Device`.
- [ ] Implement `Connection` model linking interfaces/devices.
- [ ] Add and review migrations for all core models.
- [ ] Add proof-of-concept-only data migration for test admin user `admin` / `admin123` (never for real-world deployment).

## Stage 4 — API implementation (DRF)
- [ ] Add Django REST Framework and baseline API configuration.
- [ ] Add serializers for Site, Device, Interface, Connection.
- [ ] Implement CRUD API endpoints with serializer-backed validation and error handling.
- [ ] Handle CRUD failure cases (e.g., referential-integrity violations and permission denial).
- [ ] Add API URL routing for DRF endpoints.
- [ ] Add API tests for list/detail/create/update/delete and permissions.

## Stage 5 — Website implementation (Django templates)
- [ ] Add site list/detail pages.
- [ ] Add device list/detail pages by site.
- [ ] Add interface and connection views by device.
- [ ] Add web URL routing for template views.
- [ ] Add manage actions/forms for superuser permissions at this stage.
- [ ] Add UI tests for key browse/manage flows.

## Stage 6 — Quality and operability
- [ ] Configure environment-based settings split (dev/test/prod-ready structure).
- [ ] Add linting/formatting/static checks and documented local commands.
- [ ] Add structured logging and error-handling conventions.
- [ ] Add seed/sample data for local/demo use.
- [ ] Expand test coverage for edge cases and permissions.
- [ ] Document architecture and operational assumptions.

## Stage 7 — Packaging and runnable environments
- [ ] Write complete installation and run instructions in README.
- [ ] Add Dockerfile for local runnable service.
- [ ] Add docker-compose setup for app + dependencies.
- [ ] Add one-command tester workflow to run and access UI in browser.
- [ ] Document API usage examples and smoke-test steps.

## Stage 8 — Deployment implementation (future)
- [ ] Implement ASGI deployment with Django in async-capable mode.
- [ ] Configure Gunicorn service running multiple Uvicorn workers (typically about 2x CPU cores).
- [ ] Add Nginx reverse proxy configuration.
- [ ] Add production deployment docs and rollout checklist.
- [ ] Add operational monitoring and health checks.
