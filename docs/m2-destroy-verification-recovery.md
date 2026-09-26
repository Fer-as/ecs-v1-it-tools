# M2 destroy verification recovery

The approved destroy in [run 36269051826](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36269051826)
reported `33 destroyed`. Its later cleanup step failed because the NAT lookup
used an unsupported AWS CLI option. Preserve that failed run and its logs.
Later verification is separate evidence; it does not change the original run's
conclusion.

## Original evidence identity

- Workflow commit: `119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc`.
- Binary plan: `ecs-v1/dev/plans/36269051826/1/destroy.tfplan` in
  `feras-ecs-it-tools-tfstate-670941257756`.
- S3 version: `g_pQkIpHQNCb57dmc9olKfueIskuelLw`.
- Plan SHA256: `aa6b5497978de8d61442ba5b846feb5ebe78740fa9546c22c84449d30313c86c`.
- Pre-apply application state version: `ajD_Rkcm8F_oXKif_JcdDmuW7oBPM80v`,
  encrypted with AES256.
- ECR images before apply: one.

## Verification workflow

After the verifier change and workflow are reviewed and published, dispatch
**Verify original destroy cleanup** from `main`. It has no inputs and no
Terraform apply. It runs under the existing `dev` OIDC planning role and shares
the application Terraform concurrency group.

The job downloads the original run's logs and the current object at the unique
original plan key. It requires the original workflow SHA, S3 object version and
binary SHA256 to match the values above. It checks the pre-apply state version,
encryption and ECR image count against the original apply-job log. If that
key's current version has changed, the job stops; it does not silently use a
replacement. It renders the
original plan, requires the approved 33 deletes and original NAT/EIP IDs, then
probes those resource identities. It checks managed application state, the two
application DNS records, retained hosted zone and current encrypted state
object. A fresh destroy-mode plan must have detailed exit code zero. Terraform
uses its native temporary S3 state lock for this final plan; it does not apply
or write state.

The unrelated-DNS baseline comes from the original run's **Inspect DNS before
planning** log, not the lost pre-apply verifier snapshot. The job compares
that inventory with current unrelated records and labels the source explicitly.
It cannot prove that no unrelated DNS change occurred in the interval between
the plan-job inspection and the original apply.

## Independent retained-foundation checks

The application planning role does not have access to the separate OIDC
bootstrap state or all bucket-configuration APIs. Capture these read-only
results using an authorized account session in `eu-west-2`; do not print state
contents or credential material:

```powershell
aws sts get-caller-identity
aws s3api get-bucket-versioning --bucket feras-ecs-it-tools-tfstate-670941257756
aws s3api head-object --bucket feras-ecs-it-tools-tfstate-670941257756 --key ecs-v1/dev/terraform.tfstate
aws s3api list-object-versions --bucket feras-ecs-it-tools-tfstate-670941257756 --prefix ecs-v1/dev/terraform.tfstate
aws s3api head-object --bucket feras-ecs-it-tools-tfstate-670941257756 --key ecs-v1/bootstrap/github-oidc/terraform.tfstate
aws iam get-open-id-connect-provider --open-id-connect-provider-arn arn:aws:iam::670941257756:oidc-provider/token.actions.githubusercontent.com
aws iam get-role --role-name ecs-it-tools-github-auth
aws iam get-role --role-name ecs-it-tools-github-terraform-plan
aws iam get-role --role-name ecs-it-tools-github-terraform
aws iam get-role --role-name ecs-it-tools-github-application
```

Confirm bucket versioning is enabled; the current application state object has
encryption and a non-null version different from the pre-apply version; the
pre-apply version remains in history; the bootstrap state object, OIDC provider
and roles remain. Record the command time, account, region and exit status.
These checks establish retained foundations, not an account-wide orphan audit.

Keep the evidence chain distinct: original apply succeeded, original verifier
failed, later resource verification passed or failed, and independent retained
foundation checks passed or failed. Begin final recreation only after reviewing
all of those results.
