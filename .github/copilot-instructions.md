# Agent Development Instructions (Python / Django / DRF)

## Core engineering practices
- Keep changes small, focused, and reversible.
- Prefer explicit, readable code over clever shortcuts.
- Follow existing project structure and naming once scaffolding is introduced.
- Do not add placeholder comments in empty `__init__.py` files.

## Definition of done for PRs
- For every future PR, update relevant documentation when needed.
- This includes agent-facing docs, developer-facing docs, and user-facing docs impacted by the change.
- Keep PR titles short and direct (for example: `Add code data models`) without extra technical detail.
- Keep the main PR description/comment updated to reflect the current state of the full PR, not only the latest commit.

## Python practices
- Target modern Python with type hints for public functions and methods.
- Use dataclasses/typed structures where they improve clarity.
- Validate inputs at boundaries and fail with clear exceptions.
- Avoid hidden side effects in helpers and model methods.

## Django practices
- Keep business logic out of views when possible (services/selectors/managers as needed).
- Keep models focused on domain invariants and relationships.
- Use migrations for every schema change; never edit applied migrations.
- If iterative PR updates produce multiple new migrations for the same model change set, consolidate them into one migration before merge.
- Use Django admin for operational management where required.
- In Django admin, use `raw_id_fields` for all foreign keys.

## DRF practices
- Use serializers for validation and representation; do not duplicate validation in views.
- Apply explicit permission classes and role-aware access controls.
- Keep ViewSets/APIViews thin and delegate domain logic.
- Prefer deterministic API responses and stable field naming.
- **Docstrings are user-facing**: DRF-Spectacular automatically includes ViewSet, serializer, and action docstrings in the generated OpenAPI schema and renders them in the Swagger UI and ReDoc browser interfaces.  Any docstring on a DRF component is therefore public-facing documentation.  Write them for API consumers, not for internal developers.  Do not include implementation notes, TODO markers, "PoC" caveats, or debugging context in docstrings; those belong in code comments or developer documentation only.

## Testing practices
- Write tests close to behavior changes and keep them deterministic.
- Use Django/DRF test tools for request/response and permission coverage.
- Organize app tests in `tests/` packages (with `__init__.py`) so Django test discovery finds `test*.py` modules automatically.
- Name Django `TestCase` classes with a `Test` prefix (for example, `TestSiteModel`) and keep names explicit.
- Keep tests class-based and group them either by model (for model behavior/methods) or by function/feature under test.
- Cover role-based access (engineer manage vs customer read-only).
- Mock external systems in unit tests; avoid network calls in default test runs.
- Use the Django test runner/style (`python manage.py test`), not pytest, for this repository.
- Run relevant tests before submitting changes.
- **Test anonymous access**: every endpoint test class must include tests that verify unauthenticated (anonymous) requests are rejected with the correct status code.
- **Assert database state**: after a create or update operation, do not only assert the HTTP response; also fetch the record from the database and assert that the stored values match the submitted payload.
- **Assert complete error messages**: when testing validation errors, assert the full error message string exactly as returned by the API, not just the presence of the error key.

## Formatting practices
- Follow PEP 8 formatting conventions.
- Keep `isort` and `black` available in dependencies and use them for formatting.
- On every change, run formatters in this order on touched files (excluding migrations): `isort`, then `black`.

## Documentation writing
- Explanations must explain implications and tradeoffs in plain language; do not only mention high-level terms without context.
