# Terraform deployment and recreation

This is the established GitHub Actions procedure for AWS account `670941257756`, region `eu-west-2`, hostname `tm.feras-dev.co.uk`. The final M3 recreation succeeded in [publication run 36272693835](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36272693835) and [deployment run 36273089001](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36273089001). The observations below are dated evidence, not a live availability promise.

The application Terraform root is `terraform/`, default workspace, S3 backend bucket `feras-ecs-it-tools-tfstate-670941257756`, state key `ecs-v1/dev/terraform.tfstate`. `terraform/backend.tf` sets `encrypt = true` and `use_lockfile = true`. The existing hosted zone `Z01014153ETFBQT2QXXK2`, backend bucket/history, and separate `bootstrap/github-oidc` state are retained foundations. Do not create another hosted zone or migrate this state to complete application deployment.

## Reproduction order after an approved clean destroy

1. Confirm the selected `main` source revision, AWS account/region, retained backend and hosted zone, and current application state. A historical image tag or plan is not proof of current ECR contents.
2. In **Actions → Terraform deployment → Run workflow**, select branch `main`, `operation: ecr-bootstrap`, `image_tag: <selected full 40-character source SHA>`, `image_digest: blank`, `apply: true`. Review the generated ECR-only saved plan before personally approving `dev-terraform-apply`. This targeted stage creates the repository; it does not publish an image.
3. In **Actions → Application build and publish → Run workflow**, select `main`. This workflow has no dispatch inputs. It tags the `linux/amd64` image with the exact dispatch commit (`github.sha`), runs container `/health` and HTML smoke checks, pushes to `ecs-it-tools`, and reports the ECR digest. Record the source SHA, immutable tag, digest, platform and run URL. If the source SHA differs from the ECR-bootstrap placeholder, use the actually published SHA and digest for full deployment.
4. In **Actions → Terraform deployment**, select `main`, `operation: certificate-bootstrap`, the published full `image_tag`, blank `image_digest`, and `apply: true`. Review the certificate-only saved plan and approve its apply gate. This stage does not manually add a DNS record or start the service. Inspect the certificate and existing validation record before the full plan; do not blindly import or request a duplicate certificate.
5. In **Actions → Terraform deployment**, select `main`, `operation: deploy`, the published full `image_tag`, its exact `sha256:` ECR digest, and `apply: true`. Review the complete plan and retained-resource boundary before approving `dev-terraform-apply`. Terraform creates the validation CNAME, completes ACM validation, then creates the HTTPS listener; `module.alb` consumes `aws_acm_certificate_validation.this.certificate_arn`. The private ECS service starts from the verified ECR image.
6. Preserve each run URL, workflow/source SHA, plan SHA256, S3 key/version, approval and apply result. Check service steady state, running task image/digest and private networking, ALB target, CloudWatch logs, ACM status/use, HTTPS `/health`, HTTP redirect, browser page and post-apply no-change plan. A plan-only run is not an apply, and apply success alone is not runtime acceptance.

The deployment workflow checks out its exact dispatch commit, verifies the account and OIDC planning/apply role, runs Terraform 1.16.2 with the committed provider lockfile, stores a binary plan at a unique versioned S3 key, and rechecks its SHA256 and scope after download. The apply job uses `dev-terraform-apply`; `terraform-application-dev` concurrency has `cancel-in-progress: false`. The saved plan contains its input values. Review a changed or stale plan afresh; do not reuse an applied or obsolete plan.

### Validation-record ownership

Before a full apply, compare the certificate's current DNS validation name,
type and value with the actual hosted-zone record and Terraform state. If a
matching record already exists outside state, stop and review a focused import
of **that record only** into `aws_route53_record.certificate_validation`; do
not import the hosted zone or enable blind overwrite. If the record is absent,
the normal full plan creates it. If it differs, resolve the discrepancy before
approving the plan. The M3 recreation followed the absent-record path.

## Final M3 identity and observed result

- Source/image tag: `f91e4e9c942a94f0c37388acd6948366e80afefa`.
- ECR/task digest: `sha256:ccf22a730439f38a4c56912f6b61425ce07cb2a2e49dbd6010e8d3b097b9e1be`.
- Full deployment plan: `ecs-v1/dev/plans/36273089001/1/deployment.tfplan`; S3 version `icaDnV68cy4OukCBWRX4ink7orwHYi1P`; SHA256 `91a7dcadf2bb3eba5e02391c0672af0a0fd8fd7f62969370e4e0fd8578332785`.
- [Final runtime capture](evidence/terraform/2026-09-26-m3-final-aws-runtime.txt): service 1 desired/1 running/0 pending; task on private subnet with public IP assignment disabled; ALB target Healthy; ACM Issued and in use; ECR tag/digest recorded. ECS task `healthStatus` was `UNKNOWN`, not `HEALTHY`.
- [HTTP capture](evidence/terraform/2026-09-26-m3-final-http.txt): HTTPS `/health` returned 200, `application/json`, `{"status":"ok"}`; HTTP redirected 301; root page returned HTML.
- [Workflow metadata](evidence/terraform/2026-09-26-m3-workflow-identities.json): the unmasked `Verify no remaining infrastructure changes` step concluded success. Its command is `terraform plan -detailed-exitcode`; full step output was not downloaded.

For deletion scope and the original M2 verifier failure, use the [destroy runbook](terraform-destroy-workflow.md) and [recovery record](m2-destroy-verification-recovery.md). The [evidence index](evidence/README.md) distinguishes all lifecycle revisions and local artifacts.
