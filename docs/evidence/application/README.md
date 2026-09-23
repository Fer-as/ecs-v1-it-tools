# Application pipeline evidence — 23 September 2026

Baseline: CT-2026-09-22-02.
Verification level: Development runtime verification.
Independent runtime acceptance remains pending.

## Implementation and run

- Implementation PR: https://github.com/Fer-as/ecs-v1-it-tools/pull/1
- Implementation commit: 445ee3220cd99245755f6ea12f71f5b94cc80bb7.
- Merged workflow/source commit: 1c7747cb376d54351f98073e39ef0f72c8ff813c.
- Claude passed staged tree: 2de479b4f568ae50d54593d0b9624108113d09d4.
- Run: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/35843986916
- Trigger: workflow_dispatch, main branch, dev environment.
- Result: success; displayed total duration 2m 6s.
- Account: 670941257756. Region: eu-west-2.

## Evidence files

| File | Result |
| --- | --- |
| [Application role apply](../oidc/20260923-103607-application-role-apply.txt) | 2 added, 0 changed, 0 destroyed; exit 0 |
| [Complete publish job log](2026-09-23-application-run-35843986916.txt) | Build, local smoke checks, OIDC authentication, push and image verification passed |
| [Run screenshot](../../screenshots/2026-09-23-application-pipeline-success.png) | Success status and publication summary |

## Verified publication

Image:
670941257756.dkr.ecr.eu-west-2.amazonaws.com/ecs-it-tools:1c7747cb376d54351f98073e39ef0f72c8ff813c

Digest:
sha256:7dbfb5a3e69b389bf1e1f573609b19b4c245b24d03f8bd9c9bffa076ff6e77f6

- Checked-out source matched the full commit-SHA image tag.
- Built image platform: linux/amd64.
- Container user: appuser.
- Source revision label matched the image tag.
- Local HTTP /health returned 200 and {"status":"ok"}.
- Local application page returned HTML successfully.
- GitHub OIDC assumed ecs-it-tools-github-application.
- AWS identity matched account 670941257756 and session application-35843986916.
- Repository inspection confirmed IMMUTABLE tags and an unused source tag.
- Docker push digest matched ECR.
- Digest-addressed image inspection matched the tested local image ID.

The digest-addressed pull may reuse local cache; this is not evidence
of a cache-independent download.

## Provenance

The complete log was extracted unchanged from 0_publish.txt in the
GitHub-downloaded archive.

Original extracted size: 104387 bytes.
Original extracted SHA256:
CF1E66425FBD1517B37838867AA4CA9E796A8A05A15F9216EA95E121D512AAE4

The original ZIP remains outside the staged evidence package.
The hash describes the original extracted bytes; Git may normalize
text line endings. Runtime warnings and ANSI formatting are retained. Trailing spaces and tabs were removed from the repository copy; command results were unchanged. The original extracted hash above applies before this normalization.

## Scope and remaining work

This run published an image. It did not deploy it to ECS or change
the application's Terraform image selection.

The local HTTP smoke checks do not satisfy the deployed HTTPS health
gate or its required demonstrated unhealthy-path failure.

The publishing role is managed in the separate OIDC bootstrap state.
It has repository-scoped ECR permissions and requires the repository
to exist before publication.

Existing immutable tags cause the workflow to fail explicitly.
That rejection path has not yet been demonstrated by a runtime test.

The pinned actions emitted a Node runtime deprecation warning.
Repository scan_on_push is enabled, but scan findings are not enforced
as a pipeline gate.

Pending:
- Independent runtime evidence acceptance.
- Terraform deployment and destroy pipelines with successful run evidence.
- Automated deployed HTTPS health gate and unhealthy-path failure evidence.
