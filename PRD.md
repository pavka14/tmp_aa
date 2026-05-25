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


### API permission design (demo-grade)
- Write operations on all API endpoints are guarded by an `IsSuperUser`
  permission class that returns `True` only when the requesting user is a
  Django superuser, and `False` otherwise.
- This is intentionally a temporary, demo-grade solution.  In a
  production system, permissions should be expressed as group-based roles
  (e.g. a `Network Engineers` group with explicit per-model/action grants)
  rather than relying on superuser status, which bypasses all permission
  checks and is too coarse-grained for a real deployment.  See Limitations
  for the corresponding constraint.

### API serializer validators (proof-of-concept)
- The `SiteSerializer` applies an API-level name length constraint:
  minimum 4 characters, maximum 40 characters.
- The underlying `Site` model field allows up to 64 characters.  This
  demonstrates that the API layer can enforce a stricter contract than the
  database layer.  These two validation layers are intentionally
  independent: models guard database integrity; serializers shape the API
  contract.  This is a proof-of-concept example only; production-grade
  APIs should align model and serializer constraints to avoid confusion.

### Connection tracing endpoint
- `GET /api/v1/connections/traced/?type=<type>&id=<id>` returns all active
  connections that touch the specified site, device, or interface on either
  their start or end endpoint.  The response includes the traced object's
  type, id, and name, plus a count and full list of matching connections
  with nested start/end endpoint representations (site → device →
  interface hierarchy).
- For this proof-of-concept, Django serves the web pages and static files directly.
- Modal open/close behavior in the static website pages is implemented with Bootstrap 5 built-in modal functionality (no HTMX required for this step).
- For production deployment, static assets should be collected to a dedicated directory and served directly by Nginx instead of Django.

### Connection create/update payload structure
- Create and update payloads for the Connection endpoint use a nested tuple
  structure for the two endpoints instead of flat FK fields:
  ```json
  {
    "connection_id": "CONN-001",
    "status": "Connected",
    "start": {"site": 1, "device": 2, "interface": 3},
    "end":   {"site": 4, "device": 5, "interface": 6}
  }
  ```
  `site` is required in both objects; `device` and `interface` are optional.
- FK values are resolved against the **active** record set only; attempting to
  reference a soft-deleted site, device, or interface produces a 400 error.
  This validation is automatic because `ActiveManager` (the default manager)
  filters to `active=True`, so `PrimaryKeyRelatedField` never finds
  soft-deleted rows.

### API partial-update (PATCH) behaviour
- DRF's standard `PATCH` semantics mean that any field omitted from the
  payload keeps its current value on the instance.  For the nested `start`/
  `end` connection endpoint objects this is intentional: a PATCH payload that
  supplies only `start` leaves the `end` endpoint unchanged.
- This is a *delta* model: the payload represents the change to apply, not
  the complete new state of the record.  The full six-field state (both
  endpoints) is always validated by `Connection.clean()` after merging, so a
  partial payload cannot create an inconsistent record.
- The trade-off: callers must be aware that omitting a field in a PATCH
  request does not clear it.  To clear an optional FK field (e.g. remove a
  device from an endpoint) the field must be explicitly sent as `null`.
  In a production API this behaviour should be clearly documented in the
  OpenAPI schema and tested against consumer expectations.

### Docstrings and user-visible text
- DRF-Spectacular introspects ViewSet and serializer docstrings at runtime
  and exposes them verbatim in the OpenAPI schema, in the Swagger UI, and in
  ReDoc.  This means **any docstring on a ViewSet, serializer, or action is
  effectively user-facing documentation**.  Docstrings must therefore be
  written with the same care as any other public-facing content: accurate,
  complete, professional, and free of internal implementation notes that
  could mislead API consumers.  Do not leave debugging notes, provisional
  language ("TODO", "PoC"), or internal-only commentary in docstrings.

### Access Channels
- **Website**: a simple Django-rendered website.
- **API**: a Django REST Framework (DRF) API exposing equivalent data and operations.

### Django REST Framework (DRF)
DRF is a widely-used, mature library that adds REST API capabilities on top of
Django.  It provides serializer classes (schema + validation), generic view
classes (list, retrieve, create, update, delete), authentication and permission
hooks, a browsable API renderer, and router-based URL registration.  All API
endpoints in this application are built using DRF ModelViewSets backed by DRF
ModelSerializers.

### DRF-Spectacular
DRF-Spectacular is an OpenAPI 3 schema-generation library for DRF.  It
introspects ViewSets, serializers, and docstrings at runtime to produce a
standards-compliant OpenAPI schema without any manual annotation required.
From that schema it renders two interactive browser UIs — Swagger UI and
ReDoc — that let users authenticate and make live API requests directly from
the browser.

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
- A proof-of-concept data migration creates an `admin`/`admin123` superuser for local/demo convenience.  API tests deliberately do **not** use this account: it is not guaranteed to exist in all environments (a fresh deployment without that migration applied would not have it), and relying on migration-created credentials in tests would make the test suite brittle.  Each test class creates its own superuser via `User.objects.create_superuser` instead.
- Tests for the static website currently omit explanatory comments because they are intentionally simple and self-explanatory. In a production-grade test suite, each test should describe what it validates and why.
- **API authentication**: The API currently uses Django session authentication (cookie-based). Alternatives include API Key authentication (simple, but requires key management infrastructure), Bearer/JWT tokens (stateless, but requires token issuance, rotation, and revocation logic), and OAuth 2.0 (the most complete and standards-compliant approach, supporting delegated access and fine-grained scopes). OAuth 2.0 is considered overkill for a demo because it requires additional infrastructure: an authorization server, token store, client management, refresh-token rotation, and scope definitions. Session auth is acceptable for this PoC where all access is first-party and browser-based.
- **API permission model**: Write access is currently guarded solely by Django's superuser flag (`is_superuser`). This is a demo-grade shortcut. A production-ready system should use group-based role permissions (e.g. a `Network Engineers` group with explicit per-model write grants) so that write access can be granted to non-superuser accounts without giving them full administrative privileges.
- **API-level validators**: The `SiteSerializer` enforces a name length window (4–40 characters) that is stricter than the underlying model field (max 64). This is a proof-of-concept demonstration of layered validation. In production, model and serializer constraints should be aligned or the stricter constraint should live in the model so it is enforced consistently across all code paths.

## Future developments
- Replace temporary superuser-only write access with group-based permissions.
- Add a data migration that creates a `Network Engineers` group for assignable engineer permissions.
- Add serializer-driven CRUD error handling patterns for referential integrity violations and authorization failures.
- Add a proof-of-concept-only data migration to create an `admin` user with password `admin123` for tester convenience.
- The `admin/admin123` migration is strictly for proof-of-concept use and must never be used in real-world deployment.
- **TODO (out of scope)**: All list endpoints currently return all matching records (up to the page size of 100). They need additional query parameters for client-controlled ordering (e.g. `?ordering=name`), per-request page size limits, and keyword search/filtering. These features require adding filter backends (e.g. `django-filter`, DRF `SearchFilter`, `OrderingFilter`) and are deferred to a future stage.
