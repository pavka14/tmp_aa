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

## Deployment Direction (Planning)
Possible approaches considered:
1. Traditional synchronous Django + WSGI stack.
2. Async-capable Django deployment using ASGI.
3. Container-centric orchestration with reverse proxy ingress.

Selected direction:
- **Async Django (ASGI)** to support long-term expansion toward asynchronous network-device operations initiated from Django views.
- **Uvicorn service running multiple Gunicorn workers**, fronted by **Nginx** reverse proxy.

Implementation status:
- Deployment implementation is **out of scope** for this onboarding issue.

## Future developments
- Replace temporary superuser-only write access with group-based permissions.
- Add a data migration that creates a `Network Engineers` group for assignable engineer permissions.
- Add serializer-driven CRUD error handling patterns for referential integrity violations and authorization failures.
- Add a proof-of-concept-only data migration to create an `admin` user with password `admin123` for tester convenience.
- The `admin/admin123` migration is strictly for proof-of-concept use and must never be used in real-world deployment.
