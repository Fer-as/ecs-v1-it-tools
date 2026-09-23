terraform {
  required_version = "~> 1.16.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.36.0"
    }
  }

  backend "s3" {
    bucket       = "feras-ecs-it-tools-tfstate-670941257756"
    key          = "ecs-v1/bootstrap/github-oidc/terraform.tfstate"
    region       = "eu-west-2"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region              = "eu-west-2"
  allowed_account_ids = ["670941257756"]
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]

  tags = {
    Project = "ecs-it-tools"
    Purpose = "GitHub Actions authentication"
  }
}

data "aws_iam_policy_document" "github_dev_trust" {
  statement {
    sid     = "GitHubDevEnvironment"
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
        "repo:Fer-as/ecs-v1-it-tools:environment:dev"
      ]
    }
  }
}

# GitHub environment dev restricts deployment branches to main.
# This role intentionally has no attached permission policies.
resource "aws_iam_role" "github_auth" {
  name                 = "ecs-it-tools-github-auth"
  description          = "GitHub OIDC authentication proof for the dev environment"
  assume_role_policy   = data.aws_iam_policy_document.github_dev_trust.json
  max_session_duration = 3600

  tags = {
    Project = "ecs-it-tools"
    Purpose = "GitHub Actions authentication proof"
  }
}

output "github_oidc_provider_arn" {
  value = aws_iam_openid_connect_provider.github.arn
}

output "github_auth_role_arn" {
  value = aws_iam_role.github_auth.arn
}