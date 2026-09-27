# M3 final healthy deployment evidence inventory

Captured: 2026-09-26T22:08:25.7222161Z (UTC). AWS account 670941257756; region eu-west-2.

- Source/image tag: f91e4e9c942a94f0c37388acd6948366e80afefa
- ECR/task digest: sha256:ccf22a730439f38a4c56912f6b61425ce07cb2a2e49dbd6010e8d3b097b9e1be
- M3 publication: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36272693835 (attempt 1, success)
- M3 full deployment: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36273089001 (attempt 1, success)
- M2 read-only recovery: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36271972985 (attempt 1, success)
- M3 saved-plan key: ecs-v1/dev/plans/36273089001/1/deployment.tfplan
- M3 saved-plan S3 version: icaDnV68cy4OukCBWRX4ink7orwHYi1P
- M3 saved-plan SHA256: 91a7dcadf2bb3eba5e02391c0672af0a0fd8fd7f62969370e4e0fd8578332785 (recomputed from the exact S3 object version)

| New evidence file | Scope | SHA256 of current local evidence file |
| --- | --- | --- |
| [2026-09-26-m3-final-http.txt](2026-09-26-m3-final-http.txt) | Live HTTPS /health, HTTP redirect, root HTML | 8b62ea3d21d2d2e68e3bcadd61fdf55966d0141a413767fefbcc16a53f60720b |
| [2026-09-26-m3-final-aws-runtime.txt](2026-09-26-m3-final-aws-runtime.txt) | ECS task/service, ALB, ACM, ECR, networking | 57fd28dff546112cf95e692dfa7c4d938fe414eebbdcb33c5e76666e3efefe20 |
| [2026-09-26-m3-final-cloudwatch.txt](2026-09-26-m3-final-cloudwatch.txt) | Exact final-task CloudWatch startup and access excerpts | 88d4f5ece51b1fb391bc65bf366a66ff0d8569328859274f0bf4664dd1cdb724 |
| [2026-09-26-m3-retained-backend.txt](2026-09-26-m3-retained-backend.txt) | S3 versioning, encryption, public-access flags and retained state versions | ce4d697d0afd9e56b895b4d549d03aa16854c4a2c63ec7f79f746de432ef7fcd |
| [2026-09-26-m3-workflow-identities.json](2026-09-26-m3-workflow-identities.json) | M2 recovery/M3 publication/deploy run IDs, job steps and saved-plan hash | 5aed9e68044649bb00849f8129bb1ce6a3e533f7a8d62884d7421cfe087567bf |

These hashes describe the current working-tree evidence files, not Git-normalized
staged blobs. Before final commit, trailing whitespace in the HTTP capture and
an extra blank line at the backend capture's EOF were removed. These
whitespace-only corrections did not change the recorded HTTP or AWS results.

The deployment run's unmasked Verify no remaining infrastructure changes step concluded success. Its command uses terraform plan -detailed-exitcode; a successful step supports a zero-exit no-change result. Full GitHub step logs were not downloaded.

The ECS task reports healthStatus=UNKNOWN; service deployment completion and the correlated ALB target's healthy state were independently captured. ECR metadata shows the digest and Docker v2 manifest type; task runtime shows LINUX/X86_64. A standalone ECR platform-manifest inspection was not captured.

CloudWatch evidence comes from the final task's exact log stream. IPv4-shaped strings in recent access messages were replaced with REDACTED_IP, including some browser-version text; timestamps, request paths and HTTP statuses remain. Original CloudWatch events remain in AWS.

Still to capture manually: browser screenshot of the final root application with URL and capture time; if required for audit, the GitHub run summary/full step log showing the no-change message and publication platform result. No screenshots were fabricated.