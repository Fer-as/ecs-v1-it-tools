\# Terraform image-changing deployment — 24 September 2026



Baseline: CT-2026-09-22-02.



Status: development runtime verified from complete job logs.

Independent pipeline runtime acceptance remains pending.



\## Run identity



\- Run: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36064004230

\- Workflow commit: b2da1c81729398b7e792b97401f7fadde64471a9

\- Image tag: b2da1c81729398b7e792b97401f7fadde64471a9

\- Image digest: sha256:ee6457ccb42c7ab23c4bba131b6243851b9faf00989b24296e6701d87395bf98

\- AWS account: 670941257756

\- Region: eu-west-2



\## Evidence



\- \[Plan log](2026-09-24-deploy-36064004230-plan.txt)

\- \[Apply log](2026-09-24-deploy-36064004230-apply.txt)

\- \[Successful run screenshot](../../screenshots/2026-09-24-terraform-mutating-deploy-success.png)



\## Verified results



\- Retrieved saved plan passed its checksum verification.

\- Terraform apply completed: 1 added, 1 changed, 1 destroyed.

\- Task definition was replaced and the ECS service updated.

\- Running task used task-definition revision :5.

\- Running image tag and digest matched the selected published image.

\- Readiness polling was exercised during an actual rollout:

&#x20; four checks reported IN\_PROGRESS before verification passed.

\- Task private IP: 10.0.11.143; no public IP.

\- Matching ALB target was healthy.

\- Retrieved 19 log events; this verifies log availability, not log cleanliness.

\- HTTPS health gate passed with HTTP 200 and the expected JSON.

\- Post-apply Terraform plan reported no changes.



\## Failure and recovery context



Run 36060727673 completed the preceding image-changing apply but failed

its immediate readiness check before ECS reported deployment completion.



The readiness polling fix passed independent code review and was merged

at b2da1c81729398b7e792b97401f7fadde64471a9.



Recovery run 36062614321 passed all verification gates with a no-change

apply. The present run additionally exercises an actual image-changing

deployment and the polling behavior.



\## Original log provenance



Original archive retained locally:

2026-09-24-deploy-36064004230.zip



Original extracted files, before normalization:



| Archive entry | Bytes | SHA256 |

|---|---:|---|

| 1\_plan.txt | 53446 | D16FC902EF81988E7E29D613B1D58D0A9368B2C7A05B6FCE9684001328F5CAC1 |

| 0\_apply.txt | 46119 | 650F3C5C5AADB541C31FF3589F834616919AB47429D64FC4D1D52E25461C8132 |



Repository copies have trailing spaces and tabs removed.

Git may normalize line endings. The hashes above identify the original

extracted files, not the normalized repository copies.

The original ZIP remains unchanged.



\## Remaining boundaries



\- Independent pipeline runtime acceptance remains pending.

\- Terraform destroy automation and its runtime verification remain outstanding.

\- A genuine unhealthy-deployment demonstration remains outstanding.

\- Earlier readiness-review advisories remain open.

\- Earlier independently accepted lifecycle findings remain unchanged.

\- This run does not establish final submission readiness.
