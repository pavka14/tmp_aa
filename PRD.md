# Product Requirements Document (PRD)

## Product Overview
Build a Django-based service that lets users view network infrastructure and connectivity data across datacentre sites. The product serves two personas:

- **Network engineers**: can view and manage network inventory and connections.
- **Customers**: can only view network inventory and connections.

## Scope

### Core Domain Objects
- **Site**: a datacentre hosting network infrastructure.
- **Device**: a router or switch located at a site.
- **Interface**: a network interface on a device.
- **Connection**: an existing link between device interfaces.

### Functional Requirements
1. Users can access a list of sites.
2. Users can access the list of devices at a given site.
3. Users can access the list of interfaces on a given device.
4. Users can access existing connections between devices.
5. At this stage, change operations are restricted to superusers.
6. Customers have read-only access to all of the above data.

## Implementation notes

### Connection endpoint modeling
- A connection listing requirement states: "if tracking a Site, return all connections tied directly to the site, plus all connections hitting any device within that site, plus all connections hitting any interface belonging to any device within that site".
- That requirement implies device/interface endpoints may be optional for some connection records, which does not map cleanly to a single composite foreign key approach.
- Composite foreign keys are not supported in Django in a way that fits this use case.
- For proof-of-concept implementation, use explicit endpoint columns:
  - `start_site`, `start_device`, `start_interface`
  - `end_site`, `end_device`, `end_interface`
- Add model validation so interface-to-device and device-to-site hierarchy is always consistent.

### CRUD and deletion behavior
- Although CRUD APIs are planned, hard deletes are unsafe for production infrastructure inventory data.
- Referential integrity must be preserved even when records are no longer active, because connection and inventory history still depend on those relationships.
- Use soft delete semantics for core models (`Site`, `Device`, `Interface`, `Connection`) by setting:
  - `time_deleted` to current timestamp
  - `active` to `False`
- All foreign keys should use `ON_DELETE=PROTECT` to prevent accidental hard-delete cascades that would break references and erase relationship context.
- This protection is still partial because bulk database operations can bypass model-level delete logic and status transitions.

### Access Channels
- **Website**: a simple Django-rendered website.
- **API**: a Django REST Framework (DRF) API exposing equivalent data and operations.

### User and Permission Management
- End-user management workflows are out of scope for now.
- Superusers will manage users and permissions directly in Django admin.

### UI Direction
- Frontend styling will use either:
  - a ready-made theme, or
  - a Bootstrap-based custom UI.
- Final choice is TBD.

## Non-Functional Requirements
- Clear separation of read-only and manage capabilities by role.
- Consistent data model between website and API.
- Foundation ready for future asynchronous operations.
- Code formatting follows PEP 8 conventions.

## Deployment Direction (Planning)
Possible approaches considered:
1. Traditional synchronous Django + WSGI stack.
2. Async-capable Django deployment using ASGI.
3. Container-centric orchestration with reverse proxy ingress.

Selected direction:
- **Async Django (ASGI)** to support long-term expansion toward asynchronous network-device operations initiated from Django views.
- **Gunicorn service running multiple Uvicorn workers** (typically about 2x available CPU cores), fronted by **Nginx** reverse proxy.

Implementation status:
- Deployment implementation is **out of scope** for this onboarding issue.

## Assumptions and limitations
- Temporary proof-of-concept limitation: secrets are currently present in the Django settings file for convenience.
- Production-grade setup should load secrets from a separately managed `.env` (or equivalent secret manager) and keep them out of source control.
- `status` fields currently use string values for PoC compatibility. A more robust implementation should use integer constants with Django `choices`.
- Soft-delete behavior can still be bypassed by direct bulk update/delete queries outside model `delete()` usage (for example, queryset bulk operations), so it should not be treated as complete deletion governance.
- Audit trail coverage is currently missing entirely. A proper implementation should track who changed or deleted what, when it happened, why it happened, and both before/after state snapshots so actions are reviewable and reversible.
- For resilience and investigation workflows, audit data should be stored in two places: structured database models for fast querying and append-only ledger-style text logs where records are never edited in place.
- Tests currently create records per test method instead of using a shared fixture layer; a reusable general setup fixture strategy would reduce duplication, but is intentionally deferred as overkill for the current PoC stage.

## Future developments
- Replace temporary superuser-only write access with group-based permissions.
- Add a data migration that creates a `Network Engineers` group for assignable engineer permissions.
- Add serializer-driven CRUD error handling patterns for referential integrity violations and authorization failures.
- Add a proof-of-concept-only data migration to create an `admin` user with password `admin123` for tester convenience.
- The `admin/admin123` migration is strictly for proof-of-concept use and must never be used in real-world deployment.
