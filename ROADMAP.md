# ROADMAP

## Stage 1 — Repository onboarding and product definition
- [ ] Add Product Requirements Document (PRD) with roles, entities, channels, and scope.
- [ ] Add README with product overview and placeholder sections for design/assumptions/setup.
- [ ] Add deployment-options notes and selected async deployment direction (planning only).
- [ ] Add agent instructions for Python/Django/DRF and testing best practices.
- [ ] Add CONTRIBUTIONS.md with lightweight contributor expectations and test-level definitions.

## Stage 2 — Project scaffolding
- [ ] Initialize Django project and base app structure.
- [ ] Add Django REST Framework and baseline API configuration.
- [ ] Configure environment-based settings split (dev/test/prod-ready structure).
- [ ] Add baseline URL routing for web and API entry points.
- [ ] Add initial test setup and CI test command wiring.

## Stage 3 — Core data model
- [ ] Implement `Site` model and admin configuration.
- [ ] Implement `Device` model (router/switch type) linked to `Site`.
- [ ] Implement `Interface` model linked to `Device`.
- [ ] Implement `Connection` model linking interfaces/devices.
- [ ] Add and review migrations for all core models.

## Stage 4 — API implementation (DRF)
- [ ] Add serializers for Site, Device, Interface, Connection.
- [ ] Add read endpoints for all core entities.
- [ ] Add write endpoints restricted to engineer-capable roles.
- [ ] Add permission classes enforcing engineer manage/customer view-only.
- [ ] Add API tests for list/detail/create/update/delete and permissions.

## Stage 5 — Website implementation (Django templates)
- [ ] Add site list/detail pages.
- [ ] Add device list/detail pages by site.
- [ ] Add interface and connection views by device.
- [ ] Add manage actions/forms for engineer-capable roles.
- [ ] Add UI tests for key browse/manage flows.

## Stage 6 — Quality and operability
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
- [ ] Configure Uvicorn service running multiple Gunicorn workers.
- [ ] Add Nginx reverse proxy configuration.
- [ ] Add production deployment docs and rollout checklist.
- [ ] Add operational monitoring and health checks.
