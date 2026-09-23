# GitHub OIDC authentication evidence - 23 September 2026

Baseline: CT-2026-09-22-02.
Verification level: Development runtime verification.
Claude passed the configuration and authentication-proof workflow before deployment.

Implementation commit: 44a0964868e383dba1d3d89fb6a182b883405b03.
Account: 670941257756. Region: eu-west-2.

## Evidence

| File | Result |
| --- | --- |
| [Bootstrap apply](20260923-093647-bootstrap-apply.txt) | 2 added, 0 changed, 0 destroyed; exit 0 |
| [AWS inspection](20260923-093726-bootstrap-inspection.txt) | Exact provider/trust configuration; no attached or inline permission policies |
| [Complete job log](2026-09-23-oidc-proof-35838264293.txt) | Expected claims matched; OIDC role assumption and AWS identity checks passed |
| [Run screenshot](../../screenshots/2026-09-23-oidc-proof-success.png) | Successful run and PASS summary |

Run: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/35838264293
Job: https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/35838264293/job/107106891815

## Verified identity

- Trigger: workflow_dispatch.
- Branch: main.
- Environment: dev.
- Issuer: https://token.actions.githubusercontent.com.
- Audience: sts.amazonaws.com.
- Subject: repo:Fer-as/ecs-v1-it-tools:environment:dev.
- Repository ID: 1178475925.
- Owner ID: 78626961.
- Claims checked at 2026-09-23T08:38:36.205798Z.
- AWS identity verified at approximately 2026-09-23T08:38:40Z.
- Assumed role: arn:aws:sts::670941257756:assumed-role/ecs-it-tools-github-auth/oidc-proof-35838264293.

The actual run confirms the standard environment subject format.
The proof role had no attached or inline permission policies at inspection.
No static AWS keys were configured in the workflow.

## Bootstrap isolation

Terraform root: bootstrap/github-oidc.
Backend bucket: feras-ecs-it-tools-tfstate-670941257756.
State key: ecs-v1/bootstrap/github-oidc/terraform.tfstate.
The application uses a separate state key: ecs-v1/dev/terraform.tfstate.

Trust is environment-wide, not restricted to this individual workflow.
GitHub environment dev was configured to allow branch main and zero tags.
The workflow also guards the repository and ref.
A skipped job is not proof of environment-policy rejection.

## Provenance and limitations

The complete log was extracted unchanged from 0_authenticate.txt in the
GitHub-downloaded ZIP. Original extracted size: 11446 bytes.
Original extracted SHA256:
522628E6B07E03AE6674EDBDA143B33D18FFA566F77F77D86B9ECCB7957A6144

This hash describes the original extracted file bytes. Git may normalize
line endings when storing text. The original ZIP remains outside the staged
evidence package.

The log retains timestamps, ANSI formatting, GitHub-masked temporary
credentials and the runtime warning. No raw OIDC token is present.

The pinned credentials action targets Node 20; the runner reported executing
it under Node 24 and emitted a deprecation warning. The run succeeded.
Action modernization remains a follow-up.

## Pending

- Independent runtime evidence audit.
- Negative authentication tests; no rejection behavior is claimed here.
- Review of repository/environment protection before adding AWS permissions.
- Application build/push, Terraform deployment and Terraform destroy pipelines.
- Automated HTTPS health gate and demonstrated unhealthy-path failure.

This supporting authentication proof does not constitute acceptance of any
of the three mandatory project pipelines.
