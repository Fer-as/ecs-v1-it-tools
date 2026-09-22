# Terraform deployment and lifecycle evidence - 21-22 September 2026

Initial deployment baseline: CT-2026-09-21-02

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

## Initial deployment verified results

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

## Initial deployment remote-state persistence

Bucket: feras-ecs-it-tools-tfstate-670941257756

Key: ecs-v1/dev/terraform.tfstate

LastModified: 2026-09-21T17:31:48Z

Bytes: 78420

Encryption: AES256

VersionId: 4tzP4eJk_2dbCYnLb5Z0soZebQDj1lqp

Only object metadata is included; state contents are excluded.

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

Subsequent lifecycle results are recorded below.

## Lifecycle verification - 21-22 September 2026

Authorization baseline: CT-2026-09-21-03.
Verification level: Development; independent Submission Audit remains pending.
Configuration/source/image tag: ac30dd5d6c92f0acb5f7db4e0e20312c5bd7819e.
Git HEAD during recreation: 0906d8ba5532746e46840fde61e2d0e8a30773b4.
Account: 670941257756. Region: eu-west-2.
Times below use +01:00 unless explicitly marked UTC.

### Evidence index

| Evidence | Result |
| --- | --- |
| [Pre-destroy image](2026-09-21-pre-destroy-image.txt) | Accepted tag and image present before destruction |
| [Destroy apply](20260921-234743-destroy-apply.txt) | 33 destroyed; exit 0 |
| [Cleanup](20260921-235719-cleanup.txt) | Empty state; ECR/VPC/EIP/ALB/target group absent; NAT deleted; hosted zone and state history retained |
| [ECR recreation](20260922-000411-recreate-ecr-apply.txt) | 1 added; exit 0 |
| [Image build](20260922-000530-recreate-image-build.txt) | Successful cached build; linux/amd64; appuser |
| [Image push](20260922-000626-recreate-image-push.txt) | Successful push to recreated ECR |
| [Remote image](20260922-002740-recreate-image-remote.txt) | Remote linux/amd64 manifest, digest and IMMUTABLE repository verified |
| [Expired-login attempt](20260922-102944-recreate-certificate-apply.txt) | Failed backend authentication; exit 1; retained as failure evidence |
| [Certificate retry](20260922-103043-recreate-certificate-apply.txt) | After reauthentication: 1 added; exit 0 |
| [DNS inspection](20260922-103417-recreate-dns-inspection.txt) | CNAME absent; no temporary import file; no import needed |
| [Recreation plan](20260922-103455-recreate-plan.txt) | 31 additions; no changes or destroys |
| [Recreation apply](20260922-103608-recreate-apply.txt) | 31 added; exit 0; validation completed before HTTPS listener creation |
| [Recreated runtime](20260922-104155-recreated-runtime.txt) | Service, task/image, target, HTTPS, redirect, logs, ACM/DNS and state metadata |
| [Post-recreation plan](20260922-104658-recreated-post-plan.txt) | No changes; detailed exit code 0 |
| [Browser screenshot](../../screenshots/2026-09-22-recreated-it-tools-browser.png) | 189239 bytes; Development visually verified IT Tools rendered at tm.feras-dev.co.uk |

### Destroy and retained resources

Destroy ran from 21 September 23:47:43 to 23:56:02.
The repository contained the evidenced image and Terraform deleted it without
manual image removal. This demonstrates ECR force_delete for this lifecycle test.

Cleanup confirmed the retained hosted zone Z01014153ETFBQT2QXXK2 contained
NS/SOA only. Terraform-managed application A and validation CNAME records
were removed, then recreated. The hosted zone was not replaced.

Backend bucket feras-ecs-it-tools-tfstate-670941257756 and state version history
survived. The post-destroy state object was 449 bytes, AES256 encrypted,
version jLprvvNQl3f7WrQJn0xm0BbuavirSV2j. The original deployment state
version remained in the version listing.

### Recreation and runtime results

Recreation apply ran on 22 September from 10:36:08 to 10:40:55.

- Deployment: ecs-svc/7567740141603028810; COMPLETED.
- Service: 1 desired, 1 running, 0 pending, 0 failed tasks.
- Task definition: ecs-it-tools:2.
- Task: 341c4251f63842809af0081b2d3af31b.
- Private subnet: subnet-01a5f3b8fbae059f2.
- Task security group: sg-0cd73f63b3e3d9ede.
- Public IP assignment: DISABLED.
- Task private IP and healthy ALB target: 10.0.11.81:8080.
- HTTPS /health: 200 with {"status":"ok"} at 10:44:52.
- HTTP /health: 301 to https://tm.feras-dev.co.uk:443/health.
- CloudWatch startup and request logs retrieved from the recreated task.
- ACM certificate 84cdab54-b409-43d7-babc-0865a4aa17cf: ISSUED,
  DNS validation SUCCESS, attached to the recreated ALB.
- Application alias points to ecs-it-tools-alb-249009895.eu-west-2.elb.amazonaws.com.
- Post-recreation plan at 10:46:58: no changes, exit 0.

Recreated remote image index digest, matching the running task:

sha256:2d9524ed872f2c5bf9311d887188d46fa23df0ec6cd60fb51d9b9a6d5e270ac5

Runnable linux/amd64 manifest digest:

sha256:bd9d853dcb6bc04a766a73c1782aa0559eecf8af2f65f023dc744e13570cbbb1

The index digest changed from the initial deployment; the runnable manifest
remained the same and the build attestation changed.

Recreated state metadata: Modified 2026-09-22T09:40:55Z; 78397 bytes;
AES256; version HUQLSYQM1bKOtyp.3iA6nxyOsHm_CgUQ.
Only metadata is included, not state contents.

### Evidence handling and remaining work

The recreated runtime capture has 31 occurrences of the observed public
client IP replaced with REDACTED_CLIENT_IP. Its original was backed up
outside the repository. Private infrastructure addresses were retained.

The browser screenshot was initially saved under its default Screenshot
filename, then renamed. The earlier failed path lookup does not demonstrate
that no screenshot existed. LastWriteTime 22 September 10:48:27 is filesystem
metadata, not independent proof of the capture time.

Browser-image review passed at Development level. Independent Submission Audit remains pending.
OIDC and all three mandatory pipelines remain pending.

Lifecycle text captures had trailing whitespace normalized; command results were unchanged.
