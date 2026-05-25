# CONTRIBUTIONS

## Development expectations
- Keep pull requests small and focused.
- Follow Python, Django, and DRF best practices from `.github/copilot-instructions.md`.
- Prefer readable code and explicit validation.
- Add or update tests for behavior changes.

## Testing levels
- **Unit tests**: validate a small isolated unit (function/class) with dependencies mocked/stubbed.
- **Module tests**: validate multiple related units together inside one module/subsystem boundary.
- **Integration tests**: validate end-to-end behavior across subsystem boundaries.
  - Integration tests may run **without external services** (using local test doubles/containers).
  - Integration tests may run **with external services** (real database/services) when explicitly required.

## Before submitting
- Run relevant tests and confirm they pass.
- Ensure access control behavior matches requirements (engineer manage, customer view-only).
