data "aws_iam_policy_document" "github_terraform_apply_trust" {
  statement {
    sid     = "GitHubTerraformApplyEnvironment"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type = "Federated"
      identifiers = [
        aws_iam_openid_connect_provider.github.arn
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:Fer-as/ecs-v1-it-tools:environment:dev-terraform-apply"
      ]
    }
  }
}

resource "aws_iam_role" "github_terraform" {
  name                 = "ecs-it-tools-github-terraform"
  description          = "GitHub Actions Terraform application lifecycle"
  assume_role_policy   = data.aws_iam_policy_document.github_terraform_apply_trust.json
  max_session_duration = 3600

  tags = {
    Project = "ecs-it-tools"
    Purpose = "GitHub Actions Terraform application lifecycle"
  }
}

data "aws_iam_policy_document" "github_terraform_backend" {
  # Bucket listing supports backend initialization/workspace discovery.
  # Object contents and writes are restricted separately below.
  statement {
    sid       = "ListBackendBucket"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::feras-ecs-it-tools-tfstate-670941257756"]
  }

  statement {
    sid    = "ReadWriteApplicationState"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "arn:aws:s3:::feras-ecs-it-tools-tfstate-670941257756/ecs-v1/dev/terraform.tfstate"
    ]
  }

  statement {
    sid    = "ManageApplicationStateLock"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]

    resources = [
      "arn:aws:s3:::feras-ecs-it-tools-tfstate-670941257756/ecs-v1/dev/terraform.tfstate.tflock"
    ]
  }
}

resource "aws_iam_role_policy" "github_terraform_backend" {
  name   = "ecs-it-tools-terraform-backend"
  role   = aws_iam_role.github_terraform.id
  policy = data.aws_iam_policy_document.github_terraform_backend.json
}

output "github_terraform_role_arn" {
  value = aws_iam_role.github_terraform.arn
}