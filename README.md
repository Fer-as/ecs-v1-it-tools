# ECS V1 - IT Tools Deployment

This project packages [IT Tools](https://github.com/CorentinTh/it-tools)
for deployment to AWS using Docker, ECS Fargate and Terraform.

## Current status

As of 21 September 2026:

- Local Docker deployment was verified on port 8080, including `/health`.
- Manual ClickOps deployment demonstrated a running Fargate task,
  a healthy ALB target, CloudWatch logs, HTTPS health and HTTP redirection.
- The manual application infrastructure was subsequently removed.
  Its task definition became unavailable after deletion was requested.
- Terraform ECS service, ACM/DNS and ALB integration is being prepared
  and locally validated. Terraform application deployment is not yet verified.
- Project GitHub Actions pipelines and OIDC authentication remain outstanding.
  Workflows inside `app/.github/` are upstream application files.
- The application is currently offline.

## Intended architecture

The application runs in private subnets across two configured Availability
Zones in eu-west-2. The current service configuration requests one task.

- Public Application Load Balancer with HTTP-to-HTTPS redirection.
- ACM certificate for `tm.feras-dev.co.uk`.
- Route 53 A alias pointing to the ALB.
- Fargate task using Linux/X86_64, port 8080 and a non-root container user.
- Task security group permits port 8080 from the ALB security group.
- NAT gateway provides outbound connectivity for private tasks.
- ECR repository uses immutable image tags.
- CloudWatch container logs have seven-day retention.

The single task and single NAT gateway are not a fully redundant deployment.

## Local Docker execution

Run from the repository root:

```powershell
docker build --platform linux/amd64 -t ecs-it-tools ./app
docker run --rm -p 8080:8080 ecs-it-tools
```

In another terminal:

```powershell
curl.exe -i http://localhost:8080/health
```

Expected health response: HTTP 200 with `{"status":"ok"}`.

Open `http://localhost:8080` to view the application.

## Terraform

Configuration is located in `terraform/`.

- Terraform constraint: `~> 1.16.0`.
- AWS provider constraint: `~> 6.36.0`.
- Development account: `670941257756`.
- Region: `eu-west-2`.
- Hostname: `tm.feras-dev.co.uk`.

The S3 backend uses the separately bootstrapped bucket
`feras-ecs-it-tools-tfstate-670941257756`, with native S3 locking configured.

Bucket versioning, encryption and public-access protections were previously
verified. Remote-state writes and actual lock contention remain unverified.

The existing public hosted zone `Z01014153ETFBQT2QXXK2` is referenced by
Terraform as a data source. The backend bucket and hosted zone are retained
outside the application resource lifecycle.

A certificate-validation CNAME remains from ClickOps. Its ownership must
be explicitly reconciled before the first Terraform deployment.

## Deployment inputs and sequence

Run Terraform commands from the repository root using
`terraform -chdir=terraform`.

Plan and destroy operations must explicitly select both input files:

```text
-var-file=environments/dev/terraform.tfvars
-var-file=environments/dev/image.tfvars
```

The same inputs must be selected when applying without a saved plan.
When applying a saved plan, use the reviewed plan file; its inputs are
already captured.

The local, Git-ignored `image.tfvars` supplies an explicit image tag:

```hcl
image_tag = "<reviewed-implementation-commit-SHA>"
```

Replace the placeholder with the selected commit SHA. Retain this file
through destroy; do not automatically change the tag to a later HEAD.

Required deployment order:

1. Verify AWS identity, retained backend and hosted zone.
2. Review and provision the ECR bootstrap scope through Terraform.
3. Build and push the selected tagged image to that repository.
4. Verify the remote image supports linux/amd64 and record its digest.
5. Reconcile the retained DNS-validation record with Terraform ownership.
6. Review the full plan. Certificate validation must precede HTTPS
   listener creation, and the service must start using the verified image.
7. Verify running task image identity, service stability, target health,
   container logs, HTTPS `/health`, HTTP redirection and browser rendering.

The earlier ClickOps digest is historical evidence. It does not establish
the identity or availability of a future Terraform deployment image.

After destroy, recreate ECR and push/verify the selected image before
recreating the service. Destroying the application is intended to remove
Terraform-managed application DNS records and the certificate while
preserving the externally managed hosted zone and backend bucket.

The [deployment runbook](docs/deployment.md) covers bootstrap, validation-record
import and recreation. Review it before deployment. Do not perform a full apply solely because validation
passes.

## Evidence

Manual deployment evidence is stored in:

- `docs/evidence/clickops/`
- `docs/screenshots/`

The committed container-log export has a client IP redacted.

Manual deployment evidence does not prove Terraform deployment,
recreation, state locking or Terraform ECR deletion with images.

## Repository layout

- `app/`: application source and Docker configuration.
- `terraform/`: infrastructure configuration and modules.
- `docs/evidence/`: recorded command and log evidence.
- `docs/screenshots/`: visual evidence.
- `docs/diagrams/`: architecture diagram location.

## Outstanding work

- Complete review and deployment of the Terraform integration.
- Verify Terraform destroy/recreation and backend runtime behaviour.
- Implement required root project pipelines and OIDC.
- Resolve separate pre-Docker local-execution evidence.
- Complete submission documentation and evidence review.
