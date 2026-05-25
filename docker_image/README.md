This directory stores the pre-baked local Docker image archive used by README Option 2.

Expected file:
- `tmp_aa_local_image.tar` (loaded with `docker image load -i docker_image/tmp_aa_local_image.tar`)

How to refresh it after code changes:
1. `docker build -t tmp_aa:local .`
2. `docker image save -o docker_image/tmp_aa_local_image.tar tmp_aa:local`

Reminder:
- Rebuild and replace this archive with future developments so Option 2 stays in sync with the codebase.
