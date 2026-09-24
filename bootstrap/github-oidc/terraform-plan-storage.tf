data "aws_iam_policy_document" "github_terraform_plan_storage" {
  statement {
    sid    = "StoreApplicationSavedPlans"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "arn:aws:s3:::feras-ecs-it-tools-tfstate-670941257756/ecs-v1/dev/plans/*"
    ]
  }
}

resource "aws_iam_role_policy" "github_terraform_plan_storage" {
  name   = "ecs-it-tools-terraform-plan-storage"
  role   = aws_iam_role.github_terraform_plan.id
  policy = data.aws_iam_policy_document.github_terraform_plan_storage.json
}

data "aws_iam_policy_document" "github_terraform_apply_plan_storage" {
  statement {
    sid    = "ReadApplicationSavedPlans"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
    ]

    resources = [
      "arn:aws:s3:::feras-ecs-it-tools-tfstate-670941257756/ecs-v1/dev/plans/*"
    ]
  }
}

resource "aws_iam_role_policy" "github_terraform_apply_plan_storage" {
  name   = "ecs-it-tools-terraform-apply-plan-storage"
  role   = aws_iam_role.github_terraform.id
  policy = data.aws_iam_policy_document.github_terraform_apply_plan_storage.json
}