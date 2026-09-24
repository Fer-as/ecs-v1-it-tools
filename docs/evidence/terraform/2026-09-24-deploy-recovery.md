\# Terraform deployment recovery — 24 September 2026



Baseline: CT-2026-09-22-02.

Verification level: Development runtime verified; independent acceptance pending.



Run: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36021975693

Workflow commit: 12daf8f35026a62b7ee0809fc19203475e10623c.

Account: 670941257756. Region: eu-west-2.



\## Evidence



\- \[Complete planning log](2026-09-24-deploy-36021975693-plan.txt)

\- \[Complete apply log](2026-09-24-deploy-36021975693-apply.txt)

\- \[Successful run and approval screenshot](../../screenshots/2026-09-24-terraform-deploy-success.png)



\## Verified results



\- Planning and apply jobs authenticated using their separate OIDC roles.

\- Apply proceeded after approval through dev-terraform-apply.

\- Exact saved-plan retrieval and SHA256 verification passed.

\- Apply completed: 0 added, 0 changed, 0 destroyed.

\- ECS task definition: ecs-it-tools:3.

\- Image tag: 1c7747cb376d54351f98073e39ef0f72c8ff813c.

\- Image digest: sha256:7dbfb5a3e69b389bf1e1f573609b19b4c245b24d03f8bd9c9bffa076ff6e77f6.

\- Runtime platform: LINUX/X86\_64.

\- Task private IP: 10.0.11.254; no public IP.

\- ALB target health: healthy.

\- Retrieved 20 log events; this does not assert log cleanliness.

\- HTTPS https://tm.feras-dev.co.uk/health passed on its first attempt:

&#x20; certificate verification, HTTP 200 and expected JSON.

\- Post-apply Terraform plan reported no changes.



\## Failure and recovery history



Run 36016989055 failed during planning because the planning role lacked

ec2:DescribeAddressesAttribute. PR #4 added that permission; the bootstrap

policy update was applied. Planning then succeeded in run 36018883117.



Run 36019491256 created task-definition revision :3 and requested the ECS

service update, but Terraform failed while waiting because the apply role

lacked ecs:ListServiceDeployments. ECS subsequently completed the rollout.



PR #5 added ListServiceDeployments and DescribeServiceDeployments.

After applying that policy update, this recovery run generated and applied

a fresh no-change plan and passed the runtime verification steps.

The failed run's saved deployment plan was not reused.



\## Provenance



The complete logs were extracted from the GitHub-downloaded archive

2026-09-24-deploy-36021975693.zip.



Original extracted plan log:

\- Archive entry: 1\_plan.txt

\- Size: 49540 bytes

\- SHA256: 34E93C28EA38F30BFE8A2ED0273FCF261B656A7F3F076336E286DF156D05D432



Original extracted apply log:

\- Archive entry: 0\_apply.txt

\- Size: 42363 bytes

\- SHA256: DA83C2FD043CDEC187A27CE3FB73A1EA4B49A0C1833883E6B72DB3690CCD00C8



These hashes describe the original extracted bytes. Git may normalize line

endings when storing text. The original ZIP is retained locally.



\## Limitations and pending work



This successful run applied no infrastructure changes. It verifies recovery,

saved-plan application and runtime checks, but does not exercise the corrected

deployment-wait permissions during a new service update.



Still pending:

\- Successful workflow deployment with actual infrastructure changes.

\- Independent runtime acceptance.

\- Terraform destroy pipeline.

\- Unhealthy-path demonstration.

\- Final documentation and submission audit.



Node runtime deprecation warnings remain recorded in the logs.

Previously accepted lifecycle findings remain unchanged.

Repository log normalization: trailing spaces and tabs were removed from the extracted text logs. The sizes and SHA256 hashes recorded above describe the original extracted files, before normalization. The original downloaded ZIP remains unchanged and is retained locally.
