resource "aws_iam_role" "github_terraform_plan" {
  name                 = "ecs-it-tools-github-terraform-plan"
  description          = "GitHub Actions Terraform planning and inspection"
  assume_role_policy   = data.aws_iam_policy_document.github_dev_trust.json
  max_session_duration = 3600

  tags = {
    Project = "ecs-it-tools"
    Purpose = "GitHub Actions Terraform planning"
  }
}

data "aws_iam_policy_document" "github_terraform_plan_backend" {
  statement {
    sid       = "ListBackendBucket"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::feras-ecs-it-tools-tfstate-670941257756"]
  }

  statement {
    sid     = "ReadApplicationState"
    effect  = "Allow"
    actions = ["s3:GetObject"]

    resources = [
      "arn:aws:s3:::feras-ecs-it-tools-tfstate-670941257756/ecs-v1/dev/terraform.tfstate"
    ]
  }

  statement {
    sid    = "ManageApplicationPlanLock"
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

resource "aws_iam_role_policy" "github_terraform_plan_backend" {
  name   = "ecs-it-tools-terraform-plan-backend"
  role   = aws_iam_role.github_terraform_plan.id
  policy = data.aws_iam_policy_document.github_terraform_plan_backend.json
}

locals {
  # Derive inspection permissions from the explicit application policies.
  # Retain each statement's resource scope and conditions.
  # Exclude the backend policy: planning must not write state.
  terraform_plan_source_documents = [
    data.aws_iam_policy_document.github_terraform_iam.json,
    data.aws_iam_policy_document.github_terraform_services.json,
    data.aws_iam_policy_document.github_terraform_dns.json,
    data.aws_iam_policy_document.github_terraform_acm.json,
    data.aws_iam_policy_document.github_terraform_alb.json,
    data.aws_iam_policy_document.github_terraform_network.json,
  ]

  terraform_plan_source_statements = flatten([
    for document in local.terraform_plan_source_documents :
    jsondecode(document).Statement
  ])

  terraform_plan_read_statements = [
    for statement in local.terraform_plan_source_statements :
    merge(statement, {
      Action = [
        for action in try(tolist(statement.Action), [statement.Action]) :
        action
        if can(regex("^[^:]+:(Get|List|Describe)", action))
      ]
    })
    if length([
      for action in try(tolist(statement.Action), [statement.Action]) :
      action
      if can(regex("^[^:]+:(Get|List|Describe)", action))
    ]) > 0
  ]
}

resource "aws_iam_role_policy" "github_terraform_plan_inspection" {
  name = "ecs-it-tools-terraform-plan-inspection"
  role = aws_iam_role.github_terraform_plan.id

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = local.terraform_plan_read_statements
  })
}

output "github_terraform_plan_role_arn" {
  value = aws_iam_role.github_terraform_plan.arn
}