# Terraform deployment evidence — 21 September 2026

Baseline: CT-2026-09-21-02

Deployed configuration and image tag:

ac30dd5d6c92f0acb5f7db4e0e20312c5bd7819e

AWS account: 670941257756

Region: eu-west-2

Application: https://tm.feras-dev.co.uk

## Evidence files and provenance

* [Initial apply](2026-09-21-initial-apply.txt):

  original terminal output preserved from the deployment session.

  Result: 1 imported, 30 added, 0 changed, 0 destroyed.

* [Post-deployment plan](2026-09-21-post-deployment-plan.txt):

  original subsequent terminal output. Result: no changes.

  These historical files do not contain an explicit command-start timestamp.

* [Runtime capture](20260921-223912-runtime-direct.txt):

  fresh checks, not reconstructed historical outputs.

  Identity capture began at 22:39:12 +01:00; subsequent checks ran

  at 22:40:50–22:40:57 +01:00. All 12 recorded exit codes are zero.

* [Browser screenshot](../../screenshots/2026-09-21-terraform-it-tools-browser.png):

  application rendered at the expected hostname.

  Operator supplied a time marker after capture:

  2026-09-21T22:35:48.3753946+01:00.

The earlier PowerShell transcript omitted native-command output and is

excluded from this package. Direct output capture supersedes it.

Public client IPs in the captured access logs were replaced with

REDACTED_CLIENT_IP. Private infrastructure addresses were retained.

An original copy was backed up outside the repository. Trailing whitespace in the runtime capture was removed; command results were unchanged.

## Verified results

* ECS service: ecs-it-tools-service.
* Cluster: ecs-it-tools-cluster.
* Deployment: ecs-svc/4231251802616472716, COMPLETED.
* Counts: 1 desired, 1 running, 0 pending, 0 failed tasks.
* Task definition: ecs-it-tools:1.
* Task: 391967153ee54b1cb81077860a9d5b4d.
* Task subnet: subnet-000149c71fe8c0eeb.
* Task security group: sg-0555a356a5bd1262d.
* Service public IP assignment: DISABLED.
* Task private IP matches healthy ALB target: 10.0.11.19:8080.
* ECR repository: ecs-it-tools, IMMUTABLE tags.
* Remote image supports linux/amd64; task reports x86_64.
* CloudWatch startup and request logs retrieved for the running task.
* HTTPS /health returned 200 with {"status":"ok"}.
* HTTP /health returned 301 to https://tm.feras-dev.co.uk:443/health.
* ACM certificate is ISSUED, DNS validation SUCCESS, and in use by the ALB.
* Validation CNAME imported successfully; application alias points to the ALB.
* Retained hosted zone: Z01014153ETFBQT2QXXK2, with NS/SOA present.

Image index digest, matching the running task:

sha256:ba352e08804184b05387b6c81eefe2fb8eb529986fc2b60b3bd618a8d2da6de3

Runnable linux/amd64 manifest digest:

sha256:bd9d853dcb6bc04a766a73c1782aa0559eecf8af2f65f023dc744e13570cbbb1

ECS reports container/task healthStatus UNKNOWN in this capture.

The separately verified ALB target health is healthy.

## Remote-state persistence

Bucket: feras-ecs-it-tools-tfstate-670941257756

Key: ecs-v1/dev/terraform.tfstate

LastModified: 2026-09-21T17:31:48Z

Bytes: 78420

Encryption: AES256

VersionId: 4tzP4eJk_2dbCYnLb5Z0soZebQDj1lqp

Only object metadata is included; state contents are excluded.

## Pending acceptance

* Terraform force_delete with images present in ECR.
* Destroy, retained-resource survival, and recreation.
* OIDC and the three mandatory pipelines.

This evidence package does not claim these pending checks passed.

No teardown is recorded here.

## Native S3 locking verification

Verified on 21 September 2026 using Terraform 1.16.2,

the default workspace, and the existing S3 backend with use_lockfile=true.

- [Lock-holding plan](2026-09-21-lock-plan-holder-02.txt):

  started at 23:26:33 +01:00; completed with no changes and exit code 0.

- [Competing plan](2026-09-21-lock-plan-contention-02.txt):

  observed the S3 lock at 23:26:34 +01:00, then failed to acquire it

  with S3 412 PreconditionFailed and exit code 1.

- Lock ID: 01b97ce2-64fe-7b3a-123d-cc592e4bf223.

- [Normal release and retry](2026-09-21-lock-release.txt):

  no current lock object at 23:27:56 +01:00; subsequent plan

  completed with no changes and exit code 0.

Both operations were plans. No apply, manual lock deletion, or

force-unlock was used.

An earlier console-based attempt did not demonstrate contention.

A subsequent polling attempt failed because of a query error before

running the competing plan. Neither attempt is counted as a pass.

Destroy/recreation and ECR force_delete verification remain pending.
