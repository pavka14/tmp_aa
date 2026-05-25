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

### Purpose and scope of this repository
This repository is intentionally a toy repository and a crude proof of concept. Its job is to show the general approach to modelling network inventory and connectivity data in Django, not to present a finished system that is ready for real operational use. The current implementation is therefore useful as a sketch of ideas, tradeoffs, and likely future directions, but it should not be mistaken for a production design.

### Current application shape
At present, the codebase is centered on a Django web application with server-rendered views, templates, static assets, and a core data model for sites, devices, interfaces, and connections. A Django REST Framework Application Programming Interface is part of the intended architecture, but it still needs to be added. In other words, the repository currently demonstrates the website side of the concept directly in code, while the Application Programming Interface remains part of the planned next steps.

The current domain hierarchy is:
- site
- device
- interface
- connection

That hierarchy is helpful for understanding the business domain, but it also exposes why the current proof of concept is incomplete: changes higher in the tree have consequences for everything below them, and connection records are especially awkward because each connection has two ends that may be affected by upstream changes.

### Why the current implementation is not production-ready
None of the implementation in this repository should be treated as production-ready.

#### Authentication and caller trust
If and when the Application Programming Interface is added, its authentication would need to be far stronger than anything appropriate for this proof of concept. A real system would need protections such as OAuth 2.0, signed requests, Secure Sockets Layer transport, and whitelisted caller hosts. Without those controls, an infrastructure-management interface would be much too exposed.

#### Data modelling depth
The database model needs much more operational data and metadata than it currently has. For example, a serious implementation would need to track connection capacity, used capacity per port, remaining capacity per port, Virtual Local Area Network (VLAN) IDs that are taken, reserved, or free, attached interface extras such as a fibre-to-copper adapter, and other inventory details needed for safe automation and planning. The current schema only hints at the main entities; it does not yet capture the full operational state that a real system would need.

#### Deletion and referential fallout
Even in its current limited state, the model is weak because it still allows deletions without fully accounting for the fallout. If something higher in the hierarchy is deleted, related records below it can be left hanging. That is already a problem for sites, devices, and interfaces, and it is doubly problematic for a connection because a connection has two ends that both need to remain consistent. A robust design would need stronger lifecycle rules, soft deletion, archival behavior, or workflow-driven change handling so that records cannot drift into broken states.

#### Connection endpoint modelling
One explicit requirement for this proof of concept was that connection ends should carry triple foreign keys to site, device, and interface. That makes the database denormalized, which is not a **good idea**. Validations have been added as mitigation so that inconsistent combinations are rejected, but validation is only damage control here. It is not a proper substitute for a cleaner normalized design.

There is another modelling weakness as well: connections are not really interface-to-interface in the operational sense. They are from a sub-interface. The present proof of concept simplifies that detail away, which is acceptable for a sketch, but not for a system that needs to reflect real network behavior accurately.

#### Status lifecycle
Connection status handling is also too simple. A production design would need states that reflect transition and uncertainty, not just a flat notion of whether something exists. Examples include a connection being requested, being built, being in the process of being dropped, or being in an unknown state that needs investigation and repair. Those lifecycle states matter because network changes are slow, multi-step operations rather than instantaneous database updates.

### Why workflow-oriented handling matters more than raw Create, Read, Update, Delete
In practice, much of the Create, Read, Update, Delete behavior does not belong in a public Application Programming Interface at all. It belongs in views or other workflow-oriented handlers that can manage the full chain of dependent actions safely. For example, building a connection is slow and may involve multiple systems. The better approach would be for an API to request a connection, record that request in a `requested` state, and then wait while the underlying work happens. After some time, once the connection has actually been built or rejected, the result should be posted back to a callback endpoint. That approach matches the real-world shape of the operation much better than pretending that a connection can be created immediately by a single synchronous Create action.

### Current repository structure
The repository is organized to support that proof-of-concept work and its documentation:
- `src/` contains the Django code, including the current web views, templates, static assets, models, and the unit tests. The future API will also live in this code area when it is added.
- `src/infrastructure/tests/` contains the current unit and application tests.
- `.github/workflows/django-tests.yml` defines the GitHub workflow that installs dependencies, runs migrations, and executes the Django test suite.
- `.github/copilot-instructions.md` contains agent development instructions for future repository work.
- `PRD.md` contains the Product Requirements Document, which explains the intended product scope and major design assumptions.
- `ROADMAP.md` contains the implementation roadmap and is updated with each pull request so the current state of delivery stays visible.

### Technical choices and current non-goals
PostgreSQL is used because it supports transactions, proper foreign keys, partial unique constraints, and other database features that matter for a serious relational model. It would be much easier to just do it all in SQLite as a demo, but that is just not serious.

Proper deployment configuration and deployment pipelines to staging, production, and similar environments are currently out of scope. This repository is about proving the broad application shape and documenting the main design tradeoffs first; it is not yet trying to solve full delivery and operations concerns.

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
