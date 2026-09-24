data "aws_iam_policy_document" "github_terraform_iam" {
  statement {
    sid    = "ManageApplicationExecutionRole"
    effect = "Allow"

    actions = [
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:GetRole",
      "iam:GetRolePolicy",
      "iam:ListAttachedRolePolicies",
      "iam:ListInstanceProfilesForRole",
      "iam:ListRolePolicies",
      "iam:ListRoleTags",
      "iam:TagRole",
      "iam:UntagRole",
      "iam:UpdateAssumeRolePolicy",
      "iam:UpdateRole",
      "iam:UpdateRoleDescription",
    ]

    resources = [
      "arn:aws:iam::670941257756:role/ecs-it-tools-ecs-execution"
    ]
  }

  statement {
    sid    = "ManageExecutionPolicyAttachment"
    effect = "Allow"

    actions = [
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
    ]

    resources = [
      "arn:aws:iam::670941257756:role/ecs-it-tools-ecs-execution"
    ]

    condition {
      test     = "ArnEquals"
      variable = "iam:PolicyARN"
      values = [
        "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
      ]
    }
  }

  statement {
    sid     = "PassExecutionRoleToEcsTasks"
    effect  = "Allow"
    actions = ["iam:PassRole"]

    resources = [
      "arn:aws:iam::670941257756:role/ecs-it-tools-ecs-execution"
    ]

    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "github_terraform_iam" {
  name   = "ecs-it-tools-terraform-execution-role"
  role   = aws_iam_role.github_terraform.id
  policy = data.aws_iam_policy_document.github_terraform_iam.json
}