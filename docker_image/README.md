This directory stores the pre-baked local Docker image archive used by README Option 2.

Expected files:
- `tmp_aa_local_image.tar.part-00` ... `tmp_aa_local_image.tar.part-05`
- Recreate and load with:
  1. `cat docker_image/tmp_aa_local_image.tar.part-* > /tmp/tmp_aa_local_image.tar`
  2. `docker image load -i /tmp/tmp_aa_local_image.tar`

How to refresh it after code changes:
1. `docker build -t tmp_aa:local .`
2. `docker image save -o /tmp/tmp_aa_local_image.tar tmp_aa:local`
3. `split -b 95m -d -a 2 /tmp/tmp_aa_local_image.tar docker_image/tmp_aa_local_image.tar.part-`

Reminder:
- Rebuild and replace this archive with future developments so Option 2 stays in sync with the codebase.
