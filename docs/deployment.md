# Terraform deployment and recreation

Status: proposed procedure for review. Terraform application deployment
has not yet been verified.

Run PowerShell commands from the repository root. Stop after any failed
command. Review every saved plan before applying it.

## 1. Prerequisites and retained resources

- AWS account: 670941257756.
- Region: eu-west-2.
- Hostname: tm.feras-dev.co.uk.
- Existing public hosted zone: Z01014153ETFBQT2QXXK2.
- Existing backend bucket: feras-ecs-it-tools-tfstate-670941257756.
- Terraform and AWS provider versions must satisfy versions.tf.
- Docker must run Linux containers.
- Resolve blocking Development and Claude review findings before deployment.

The backend bucket and hosted zone are external prerequisites, not
application resources managed by this configuration. Preserve both during
application destroy.

The backend bucket was bootstrapped separately in eu-west-2 with versioning,
AES256 encryption and all four public-access blocks enabled. It must exist
before terraform init. If absent, restore or separately bootstrap it and
inspect any existing state before proceeding; do not silently switch to
empty local state.

Verify credentials and retained resources:

```powershell
aws sts get-caller-identity --no-cli-pager
aws s3api get-bucket-location --bucket feras-ecs-it-tools-tfstate-670941257756 --no-cli-pager
aws s3api get-bucket-versioning --bucket feras-ecs-it-tools-tfstate-670941257756 --no-cli-pager
aws s3api get-public-access-block --bucket feras-ecs-it-tools-tfstate-670941257756 --no-cli-pager
aws s3api get-bucket-encryption --bucket feras-ecs-it-tools-tfstate-670941257756 --no-cli-pager
aws route53 get-hosted-zone --id Z01014153ETFBQT2QXXK2 --no-cli-pager
aws route53 list-resource-record-sets --hosted-zone-id Z01014153ETFBQT2QXXK2 --no-cli-pager
```

Use aws login if the session has expired. Confirm the expected account.

## 2. Select the image once

After committing the reviewed implementation, record its full commit SHA.
Build from that revision with no tracked application modifications.
Inspect untracked files under app/ because they can enter the Docker context.

Create the ignored file terraform/environments/dev/image.tfvars:

```hcl
image_tag = "<full-reviewed-commit-SHA>"
```

Replace the placeholder. Retain this file through destroy and recreation.
Do not update it automatically whenever HEAD changes.

All plan commands below explicitly select the environment and image files.
Saved plans capture those inputs; their apply commands use the saved plan.

```powershell
terraform -chdir=terraform init -input=false
terraform -chdir=terraform fmt -recursive -check
terraform -chdir=terraform validate
terraform -chdir=terraform state list
```

If image.tfvars is lost, recover the selected image tag from recorded
deployment evidence or the task definition in Terraform state, then
recreate the file. Do not substitute the current HEAD automatically.
Alternatively, omit the missing image-file argument and supply
-var="image_tag=<recovered-SHA>" alongside the environment input file.

Inspect existing state before bootstrap. Do not assume it is empty.

## 3. Bootstrap ECR

The first exceptional targeted operation creates only the ECR module and
any dependencies shown in its plan.

```powershell
terraform -chdir=terraform plan -input=false -var-file=environments/dev/terraform.tfvars -var-file=environments/dev/image.tfvars -target=module.ecr -out=ecr-bootstrap.tfplan
terraform -chdir=terraform show ecr-bootstrap.tfplan
```

After reviewing that scope:

```powershell
terraform -chdir=terraform apply ecr-bootstrap.tfplan
```

Targeting is for bootstrap, not routine deployment. A full plan is required
later.

## 4. Build, push and verify the image

Read the selected commit-SHA tag directly from image.tfvars.

```powershell
$imageTag = $null
$imageInputPath = ".\terraform\environments\dev\image.tfvars"
$imageInputText = Get-Content -LiteralPath $imageInputPath -Raw -ErrorAction Stop
$imageTagMatches = [regex]::Matches(
    $imageInputText,
    '(?m)^\s*image_tag\s*=\s*"([0-9a-f]{40})"\s*(?:#.*)?$'
)

if ($imageTagMatches.Count -ne 1) {
    throw "Expected exactly one image_tag assignment containing the full reviewed commit SHA."
}

$imageTag = $imageTagMatches[0].Groups[1].Value
Write-Output "Selected image tag: $imageTag"
$repositoryUri = terraform -chdir=terraform output -raw ecr_repository_url
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repositoryUri)) {
    throw "ECR output unavailable. Inspect: terraform -chdir=terraform state show module.ecr.aws_ecr_repository.this"
}
$repositoryUri = $repositoryUri.Trim()
$imageUri = "${repositoryUri}:${imageTag}"

docker build --platform linux/amd64 --tag $imageUri .\app
docker image inspect $imageUri --format 'OS={{.Os}} Architecture={{.Architecture}} User={{.Config.User}}'

aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 670941257756.dkr.ecr.eu-west-2.amazonaws.com
docker push $imageUri

docker buildx imagetools inspect $imageUri
aws ecr describe-images --repository-name ecs-it-tools --image-ids "imageTag=$imageTag" --region eu-west-2 --no-cli-pager
aws ecr describe-repositories --repository-names ecs-it-tools --region eu-west-2 --no-cli-pager
```

Confirm linux/amd64 support and repository IMMUTABLE status. Record the tag,
registry digest and platform-manifest digest. An attestation manifest can
appear as unknown/unknown; it is not the runnable platform.

If the immutable tag already exists, inspect its identity before reuse.
Do not delete or overwrite it to bypass an identity mismatch.

The deleted ClickOps repository and its digest are historical evidence.

## 5. Bootstrap the certificate and reconcile DNS ownership

A second exceptional targeted operation creates the certificate request
without starting the ALB or ECS service:

```powershell
terraform -chdir=terraform plan -input=false -var-file=environments/dev/terraform.tfvars -var-file=environments/dev/image.tfvars -target=aws_acm_certificate.this -out=certificate-bootstrap.tfplan
terraform -chdir=terraform show certificate-bootstrap.tfplan
```

After scope review:

```powershell
terraform -chdir=terraform apply certificate-bootstrap.tfplan
terraform -chdir=terraform state show aws_acm_certificate.this
```

Use the resulting ARN with aws acm describe-certificate in eu-west-2.
Compare its DNS validation name, type and value against the actual zone.

The retained ClickOps record is:

- Name: _acc09de86e15890a1ed86e2e77a7c5dc.tm.feras-dev.co.uk.
- Type: CNAME
- Value: _c390bee1e39386102cad4f0e08909b99.wzccmgtwzk.acm-validations.aws.
- TTL: 300

If this record matches the new certificate and is not already in Terraform
state, create a temporary terraform/validation-import.tf containing:

```hcl
import {
  to = aws_route53_record.certificate_validation["tm.feras-dev.co.uk"]
  id = "Z01014153ETFBQT2QXXK2__acc09de86e15890a1ed86e2e77a7c5dc.tm.feras-dev.co.uk_CNAME"
}
```

This imports the record, not the hosted zone. Its subsequent lifecycle,
including deletion during application destroy, becomes Terraform-managed.

If the record is absent, omit the import and let Terraform create it.
If the new certificate requires a different record, stop and reconcile the
difference explicitly. Do not enable blind overwriting.

## 6. Full deployment

```powershell
terraform -chdir=terraform plan -input=false -var-file=environments/dev/terraform.tfvars -var-file=environments/dev/image.tfvars -out=dev.tfplan
terraform -chdir=terraform show dev.tfplan
```

Review resource changes, any CNAME import, account/region, private networking
and image tag. The plan must not create or replace the retained hosted zone
or backend bucket.

The configured dependency order is:

- Validation CNAME -> certificate validation -> HTTPS listener.
- Completed VPC routing and ALB module -> ECS module.
- Task definition and task security-group rules -> ECS service.

After plan review:

```powershell
terraform -chdir=terraform apply dev.tfplan
```

After confirming the CNAME import succeeded, remove the temporary import
file. It must not remain to re-import a deleted record after destroy.

Run a fresh full plan with both input files to inspect remaining changes.

## 7. Runtime acceptance

Capture and associate evidence with the deployed commit and image:

- Service desired/running counts and completed deployment.
- Running task definition, image digest and private IP.
- ALB target IP/port matching the task and Healthy status.
- CloudWatch startup and request logs.
- HTTPS /health returning HTTP 200 and {"status":"ok"}.
- HTTP redirect to HTTPS and browser rendering.

An image-index digest and its platform-manifest digest may differ; reconcile
the running digest against the recorded manifest structure.

Apply success alone does not prove these runtime criteria.

Separately verify backend state writes, actual lock contention and
Terraform ECR deletion with images. Do not infer them from configuration.

## 8. Destroy and recreate

Preserve runtime evidence and the image input file before destroy.
force_delete=true permits Terraform to delete ECR images with the repository.

```powershell
terraform -chdir=terraform plan -destroy -input=false -var-file=environments/dev/terraform.tfvars -var-file=environments/dev/image.tfvars -out=destroy.tfplan
terraform -chdir=terraform show destroy.tfplan
```

Review the deletion scope, then:

```powershell
terraform -chdir=terraform apply destroy.tfplan
```

Verify AWS cleanup and retained backend/hosted zone independently.
Preserve the state bucket and state history.

For recreation, repeat ECR bootstrap, build/push and image verification,
then certificate bootstrap and the full deployment. Recheck DNS: normally
the Terraform-managed validation CNAME will have been removed by destroy,
so no import is needed.

Rebuilding the same source SHA can produce a different digest when base
image tags or build inputs change. Record the newly verified digest each
time; a source-SHA tag alone does not establish identical image bytes.
