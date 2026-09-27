# Terraform destroy workflow

The current workflow is `.github/workflows/terraform-destroy.yml`. Its earlier
failed full destroy and partial recovery remain historical evidence. The later
M2 full destroy applied its reviewed 33-delete plan, including NAT/EIP deletion;
its post-destroy verifier failed on a CLI option. A separate read-only recovery
run passed. See [M2 verification recovery](m2-destroy-verification-recovery.md).

## EIP deletion permission

The managed network policy grants only `ec2:DisassociateAddress` in its
`DisassociateRegionalElasticAddresses` statement, using:

```text
arn:aws:ec2:eu-west-2:670941257756:*/*
```

The statement also requires `aws:RequestedRegion = eu-west-2`.

The previous statement allowed Elastic IP and network-interface resource ARNs.
During run `36129168122`, the provider attempted to disassociate the saved EIP
association after NAT deletion. The decoded authorization failure identified
the evaluated resource as:

```text
arn:aws:ec2:eu-west-2:670941257756:*/*
```

The correction matches that observed authorization resource. AWS documents
wildcards within ARN resource segments. The permission remains limited to one
action, account `670941257756`, and region `eu-west-2`, but is not limited to
this application's resources.

The derived planning policy excludes this write action. Other networking
permissions remain unchanged.

The correction was subsequently applied. In M2, the corrected path deleted
NAT gateway `nat-00d4f978d139944b2` and EIP
`eipalloc-04b6bdd1421211d2b` during the original approved apply.

## Operation

The manual `Terraform destroy` workflow runs on `main` in
`Fer-as/ecs-v1-it-tools`.

Supply the application's full image source SHA, type
`DESTROY ecs-it-tools dev`, and leave `apply` unchecked for a plan-only run.

The image SHA satisfies Terraform's required input. Destroy does not require
an image build or digest verification.

The plan uses the existing `dev` environment and planning role. It runs
`terraform plan -destroy`, permits only deletes at the 33 explicitly listed
application resource addresses, and requires an empty planned managed-resource
inventory.

A subset is permitted for partial-destroy recovery. A full destroy of the
complete application is expected to contain 33 deletions. Imports, moves,
replacements, updates, unknown addresses and deposed instances fail the guard.

Human-readable plans and resource metadata appear in public Actions logs.
The binary and text plans are stored in the existing private S3 plan prefix.

The apply job downloads the exact binary object version, checks SHA256, and
re-runs the scope guard on the downloaded plan.

Checking `apply` requests the existing `dev-terraform-apply` environment
approval. Inspect every planned resource and the deletion count before
approving. Saved-plan apply performs the reviewed deletion without another
Terraform prompt.

Both jobs check their exact AWS assumed-role identity and check out the
dispatch commit. The workflow applies only the application root, never the
bootstrap root.

Destroy and deployment share `terraform-application-dev` concurrency with
`cancel-in-progress: false`. Do not run a local application apply/destroy or
an application publication while destruction is in progress.

A pending approval holds the concurrency group. GitHub may replace an older
pending run with a newer pending run. The environment protection settings
must remain in place; they are configured in GitHub rather than by this
workflow.

## Deletion and retention

Destroy removes application resources, including populated ECR and its images,
CloudWatch application logs, ALB, ECS, NAT/EIP, VPC, ACM certificate, application
alias and certificate-validation CNAME.

The imported validation CNAME is application-managed. Its deletion and
recreation follow the lifecycle previously accepted under CT-2026-09-22-02.
The retained DNS boundary covers the hosted zone and unrelated records.

Export needed logs and image provenance before approving. Git source and
workflow files remain in the repository.

The backend bucket and hosted zone are outside the application resource
inventory. Bootstrap OIDC provider, roles and policies are in separate state,
which the application workflow roles cannot access.

The reviewed `ec2:DisassociateAddress` correction was in place for the M2
destroy. Its NAT/EIP deletion result is runtime evidence for that path.

Before apply, the verifier captures unrelated hosted-zone records, the current
state object's encryption and version metadata, and the ECR image count.

After apply it checks:

- Each approved resource using read-only AWS APIs, including EC2 IDs from the plan.
- Empty managed application state.
- Removed application DNS records and unchanged unrelated records.
- Retained public hosted zone.
- Retained current state object with server-side encryption and a non-null
  version ID; a changed version when resources were deleted.
- A subsequent destroy-mode plan with detailed exit code zero.

Known not-found API errors count as absence. Authorization errors, unexpected
errors and subprocess timeouts fail verification.

ECS task definitions can remain INACTIVE; the verifier also accepts the exact
task-definition-not-describable response after deletion. Deleted NAT gateway
and inactive cluster/service records may remain visible. No inactive
task-definition history is forcibly erased.

Cleanup polls remaining resources for at most 12 rounds with 10-second waits.
Each AWS subprocess has a 90-second timeout. The job has a 50-minute timeout;
polling is not a fixed wall-clock duration independent of API time.

The cleanup scope is the approved plan's resources, not an account-wide orphan
audit. Resources missing from state or removed by refresh drift need separate
investigation if orphan cleanup is required.

HeadObject verifies the current state object. It does not inspect bucket
versioning configuration, bucket encryption defaults, public-access settings,
or historical state versions.

Bootstrap survival is protected by scope and IAM separation, not by direct
bootstrap-state inspection.

## Observed failure and recovery

The first full destroy, run `36129168122`, planned 33 deletions. Terraform
reported 32 completed deletions before EIP deletion failed on
`ec2:DisassociateAddress`.

The failed authorization request used the generic account/region resource ARN
documented above. The earlier permission restricted to Elastic IP and
network-interface ARNs did not authorize that request.

A fresh recovery dispatch, run `36130931621`, refreshed the remaining EIP
without an association and planned one deletion. It successfully deleted the
EIP, passed cleanup verification, and produced a subsequent destroy plan with
no changes.

The recovery cleanup checked the one resource in its approved plan. It did
not retrospectively probe all 32 resources deleted by the failed run.

The successful recovery demonstrates partial-destroy recovery. It does not
retroactively make that earlier failed full run successful. The later M2 run
below tested the corrected stale-association path.

## M2 full destroy and verifier recovery — 26 September 2026

The approved [original M2 run 36269051826](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36269051826) at workflow commit
`119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc` applied the reviewed saved
plan: **0 added, 0 changed, 33 destroyed**. Its plan SHA256 was
`aa6b5497978de8d61442ba5b846feb5ebe78740fa9546c22c84449d30313c86c`,
S3 key `ecs-v1/dev/plans/36269051826/1/destroy.tfplan`, version
`g_pQkIpHQNCb57dmc9olKfueIskuelLw`. NAT and EIP deletion succeeded.

The original run then **failed** in `scripts/verify_destroy_cleanup.py verify`:
`ec2 describe-nat-gateways` was called with `--filters` instead of its singular
`--filter`. The corrected verifier was published separately. The later
[verification-only run 36271972985](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36271972985)
passed original-plan identity and 33-resource cleanup probes, application
state/DNS cleanup, retained hosted-zone/state checks, and a fresh destroy plan
with no remaining actions. Independent checks confirmed backend versioning,
encryption, state history, and separate bootstrap/OIDC foundations. The
original failed run remains failed; recovery did not rerun its destructive
plan. The unrelated-DNS comparison uses the original planning log rather
than the lost exact pre-apply verifier snapshot.

## Failure and recovery procedure

A failed apply can partially delete infrastructure. Inspect logs and actual
AWS state. Use a new workflow dispatch to create a fresh destroy plan for
any retry.

GitHub's “Re-run failed jobs” reuses the old saved-plan outputs. It is not the
recovery procedure after a partial apply. Terraform rejects a saved plan when
its state snapshot is stale.

A successful deletion followed by failed cleanup still requires investigation.
Do not bypass the cleanup checks to obtain a successful result.

Recreation uses the existing staged process:

1. Bootstrap ECR.
2. Publish an explicit source image into the recreated repository and record
   its verified digest.
3. Bootstrap the certificate and inspect DNS.
4. Run full deployment and all runtime gates.

Destroy deletes previously published image tags, so images must be rebuilt
and published before reuse. Use the newly verified digest.

## Offline validation and remaining acceptance

Run from the repository root:

```powershell
python -m unittest discover -s tests -p test_destroy_workflow.py -v
```

The tests mock AWS and Terraform calls. They do not authorize or execute a
destroy.

The initial implementation passed 10 offline tests, actionlint 1.7.12 with
ShellCheck disabled, YAML/Python parsing, and `bash -n` on all 15 shell blocks.
The 33-address inventory was compared with the Terraform source.

The independent reviewer reproduced the 10 tests, staged whitespace check,
YAML parsing, shell syntax checks and inventory comparison. Actionlint was
not independently reproduced.

The earlier configuration review accepted the resource-specific
DisassociateAddress permission. The subsequent live failure demonstrated that
it was insufficient for the stale-association request.

The corrected M2 deletion path and later cleanup recovery are evidenced above.
M3 subsequently recreated and verified the final application. Independent
submission acceptance remains separate from Development verification.

## References

- [Failed full destroy: run 36129168122](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36129168122)
- [Successful recovery: run 36130931621](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36130931621)
- [M2 original 33-delete apply, later failed verifier: run 36269051826](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36269051826)
- [M2 read-only cleanup recovery: run 36271972985](https://github.com/Fer-as/ecs-v1-it-tools/actions/runs/36271972985)
- [Terraform planning modes and saved plans](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform saved-plan apply](https://developer.hashicorp.com/terraform/cli/commands/apply)
- [ECS cluster states](https://docs.aws.amazon.com/cli/latest/reference/ecs/describe-clusters.html)
- [ECS task-definition description](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_DescribeTaskDefinition.html)
- [EC2 action and resource permissions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_ec2.html)
- [IAM Resource element and ARN wildcards](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_resource.html)
