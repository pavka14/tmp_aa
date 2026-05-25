# Agent Development Instructions (Python / Django / DRF)

## Core engineering practices
- Keep changes small, focused, and reversible.
- Prefer explicit, readable code over clever shortcuts.
- Follow existing project structure and naming once scaffolding is introduced.
- Do not add placeholder comments in empty `__init__.py` files.

## Python practices
- Target modern Python with type hints for public functions and methods.
- Use dataclasses/typed structures where they improve clarity.
- Validate inputs at boundaries and fail with clear exceptions.
- Avoid hidden side effects in helpers and model methods.

## Django practices
- Keep business logic out of views when possible (services/selectors/managers as needed).
- Keep models focused on domain invariants and relationships.
- Use migrations for every schema change; never edit applied migrations.
- Use Django admin for operational management where required.

## DRF practices
- Use serializers for validation and representation; do not duplicate validation in views.
- Apply explicit permission classes and role-aware access controls.
- Keep ViewSets/APIViews thin and delegate domain logic.
- Prefer deterministic API responses and stable field naming.

## Testing practices
- Write tests close to behavior changes and keep them deterministic.
- Use Django/DRF test tools for request/response and permission coverage.
- Cover role-based access (engineer manage vs customer read-only).
- Mock external systems in unit tests; avoid network calls in default test runs.
- Run relevant tests before submitting changes.
