# ECS v1 lifecycle evidence index

Account `670941257756`, region `eu-west-2`, hostname `tm.feras-dev.co.uk`. Run URLs are GitHub Actions records; local paths below identify files actually present in this checkout. Historical M1, failed original M2, recovered M2, final M3 and M4 identities must not be interchanged. Runtime observations are dated, not a continuous uptime guarantee.

## Lifecycle runs and immutable identities

| Milestone / evidence type | Run and revision | Plan / image identity | Local evidence |
| --- | --- | --- | --- |
| M1 ECR bootstrap, Terraform apply | [36183906907](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36183906907), workflow `119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc` | Plan SHA256 `e2680b13dad30b478e88d6eb9f8991b49b2e3dce92902bcb2281dd1fb9f28ee9`, reverified in apply-job log `108232913248`; S3 version not transcribed here | GitHub run/job logs; no local M1 plan transcript indexed |
| M1 application publication | [36185549060](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36185549060), source `119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc` | Image digest `sha256:2dc54730ab08aec68a3c7fd7b23e37f7bceb1d79eff13ceb1adb482a7746c6dd` | Run URL; separate historical [application pipeline evidence](application/README.md) is from 23 September and a different image |
| M1 full deployment / runtime | [36193925121](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36193925121), image tag `119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc` | M1 image digest above; plan identity not indexed locally | Run URL; M1 runtime result was reported separately |
| M2 destroy workflow, plan only | [36268361308](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36268361308), attempt 1, workflow `119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc` | `0` add, `0` change, `33` planned deletes; saved-plan key `ecs-v1/dev/plans/36268361308/1/destroy.tfplan`; hash/version visible in screenshot but not independently transcribed here | [Green plan-only run screenshot](../screenshots/2026-09-26-m2-destroy-plan-only-success.png); GitHub overall `success`, plan job `success`, apply job `skipped`; **no resources deleted by this run** |
| M2 original approved destroy | [36269051826](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36269051826), workflow `119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc` | 33 deletes; plan SHA256 `aa6b5497978de8d61442ba5b846feb5ebe78740fa9546c22c84449d30313c86c`; S3 key `ecs-v1/dev/plans/36269051826/1/destroy.tfplan`; version `g_pQkIpHQNCb57dmc9olKfueIskuelLw` | [Chronology and original-plan identity](../m2-destroy-verification-recovery.md). Apply succeeded; later verifier failed, so original run is failed |
| M2 read-only cleanup recovery | [36271972985](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36271972985), attempt 1, workflow `f91e4e9c942a94f0c37388acd6948366e80afefa` | Rechecked the **original** M2 plan above; fresh destroy plan had no remaining actions, not a second destructive apply | [Recovery record](../m2-destroy-verification-recovery.md), [captured run metadata](terraform/2026-09-26-m3-workflow-identities.json), [retained backend capture](terraform/2026-09-26-m3-retained-backend.txt), [recovery screenshot](../screenshots/2026-09-26-m2-destroy-recovery-success.png) |
| M3 final application publication | [36272693835](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36272693835), attempt 1, source/tag `f91e4e9c942a94f0c37388acd6948366e80afefa` | ECR/task digest `sha256:ccf22a730439f38a4c56912f6b61425ce07cb2a2e49dbd6010e8d3b097b9e1be` | [Run metadata and image identity](terraform/2026-09-26-m3-workflow-identities.json), [ECR/task runtime capture](terraform/2026-09-26-m3-final-aws-runtime.txt) |
| M3 final Terraform deployment / runtime | [36273089001](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36273089001), attempt 1, workflow/source `f91e4e9c942a94f0c37388acd6948366e80afefa` | Plan key `ecs-v1/dev/plans/36273089001/1/deployment.tfplan`; S3 version `icaDnV68cy4OukCBWRX4ink7orwHYi1P`; SHA256 `91a7dcadf2bb3eba5e02391c0672af0a0fd8fd7f62969370e4e0fd8578332785`; image digest above | [M3 inventory](terraform/2026-09-26-m3-evidence-inventory.md) and captures below; post-apply no-change step passed |
| M4 controlled runner-local HTTPS 503 rejection | [36280113216](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36280113216), attempt 1, workflow `3f335122ee57bb08ae78ae9a1780db1dd4868462` | No Terraform plan or image publication; no ECS outage | [M4 log-backed summary](m4-health-gate.md); run failed after all 12 production-gate attempts received HTTP 503 |
| M4 live healthy recovery | [36280236296](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36280236296), attempt 1, workflow `3f335122ee57bb08ae78ae9a1780db1dd4868462` | Same deployed M3 image; no Terraform plan | [M4 log-backed summary](m4-health-gate.md); overall GitHub conclusion `success`, live gate PASS; [independent post-M4 HTTP capture](terraform/2026-09-27-m4-final-http.txt) |

M2 chronology: a green destroy plan-only run saved a 33-delete plan without applying it → a later separately reviewed destructive plan was approved → Terraform destroyed all 33 resources, including NAT/EIP → original cleanup verifier failed because `describe-nat-gateways` used `--filters` instead of `--filter` → original destructive run remained failed → later verification-only recovery proved approved-resource cleanup and a no-action destroy plan → retained foundations were checked separately. The recovery DNS baseline came from the original planning log, not the lost exact pre-apply snapshot.

## Final M3 and post-M4 text captures

These files existed locally at consolidation time and are not renamed or regenerated here:

The SHA256 values in the dated M3 inventory describe the current local
evidence-file bytes, including two whitespace-only corrections made before
final commit. They do not describe Git-normalized staged blobs:
`.gitattributes` normalizes text to LF when Git stages it, and several local
captures use CRLF. The corrections did not alter substantive HTTP or AWS
results.

| Exact path | Captured evidence |
| --- | --- |
| [`docs/evidence/terraform/2026-09-26-m3-evidence-inventory.md`](terraform/2026-09-26-m3-evidence-inventory.md) | Run identities, plan version/hash, capture checksums and caveats |
| [`docs/evidence/terraform/2026-09-26-m3-final-http.txt`](terraform/2026-09-26-m3-final-http.txt) | Root HTTPS application, HTTPS `/health` 200 JSON, HTTP 301 redirect |
| [`docs/evidence/terraform/2026-09-26-m3-final-aws-runtime.txt`](terraform/2026-09-26-m3-final-aws-runtime.txt) | ECS service/task/digest/private ENI, ECR, ALB Healthy target, ACM Issued/In use, networking |
| [`docs/evidence/terraform/2026-09-26-m3-final-cloudwatch.txt`](terraform/2026-09-26-m3-final-cloudwatch.txt) | Final-task log stream and recent access records |
| [`docs/evidence/terraform/2026-09-26-m3-retained-backend.txt`](terraform/2026-09-26-m3-retained-backend.txt) | Versioning Enabled, AES256, four public-access blocks, current and preserved pre-destroy state versions, bootstrap state metadata, native-lock configuration |
| [`docs/evidence/terraform/2026-09-26-m3-workflow-identities.json`](terraform/2026-09-26-m3-workflow-identities.json) | GitHub run/step conclusions and final saved-plan identity |
| [`docs/evidence/terraform/2026-09-27-m4-final-http.txt`](terraform/2026-09-27-m4-final-http.txt) | Independent post-M4 HTTP 200, JSON content type and `{"status":"ok"}`; response Date 27 September 2026 00:15:13 GMT |

The ECS task reported `healthStatus: UNKNOWN`. The independently correlated ALB target was Healthy. The application HTTPS `/health` response returned HTTP 200 with the expected JSON. No ECS container-health `HEALTHY` claim is made. The final ECR scan was reported Complete with 17 Critical, 58 High, 41 Medium and 3 Low findings. No scan-result export is indexed here; these are disclosed counts, not a security pass. Remediation was not established as a mandatory assignment requirement.

## Available screenshots

- [Original ClickOps browser](../screenshots/2026-09-20-clickops-it-tools-browser-tm-feras-dev-co-uk.png).
- [Original ClickOps container logs](clickops/2026-09-20-clickops-container-logs.csv), with public client IP redacted.
- [Historical local Docker health](../screenshots/local-container-health.png).
- [Historical Terraform browser](../screenshots/2026-09-21-terraform-it-tools-browser.png) and [recreated browser](../screenshots/2026-09-22-recreated-it-tools-browser.png).
- [Historical application pipeline](../screenshots/2026-09-23-application-pipeline-success.png), [Terraform deployment](../screenshots/2026-09-24-terraform-deploy-success.png), and [mutating deployment](../screenshots/2026-09-24-terraform-mutating-deploy-success.png).

### Final M2/M3 screenshots present locally

- [Final IT Tools browser](../screenshots/2026-09-26-m3-final-it-tools-browser.png).
- [M3 application publication pipeline](../screenshots/2026-09-26-m3-application-pipeline-success.png).
- [M3 Terraform deployment pipeline](../screenshots/2026-09-26-m3-terraform-deploy-success.png).
- [M2 green Terraform destroy plan-only run](../screenshots/2026-09-26-m2-destroy-plan-only-success.png); apply was skipped.
- [M2 destroy verification recovery](../screenshots/2026-09-26-m2-destroy-recovery-success.png).
- [M3 ECS service steady state](../screenshots/2026-09-26-m3-ecs-service-steady-state.png).
- [M3 task-definition image tag](../screenshots/2026-09-26-m3-task-definition-image-tag.png).
- [M3 running task](../screenshots/2026-09-26-m3-running-task.png).
- [M3 final ECR image](../screenshots/2026-09-26-m3-ecr-final-image.png).
- [M3 ACM Issued and in use](../screenshots/2026-09-26-m3-acm-issued-in-use.png).
- [M3 ALB target Healthy](../screenshots/2026-09-26-m3-alb-target-healthy.png).

All eleven final screenshot paths above exist locally. The older dated M3 inventory reflected its capture-time state: its screenshot-gap statement was superseded by the later final screenshot captures linked here. These paths are the authoritative final visual evidence. No contemporaneous pre-Docker local execution screenshot or log was found. Early README history supplies local-run instructions but does not demonstrate that they were executed. An ECR scan export is not indexed here. Independent final submission acceptance remains outstanding.
