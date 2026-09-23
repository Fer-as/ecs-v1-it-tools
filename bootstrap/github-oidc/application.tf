resource "aws_iam_role" "github_application" {
  name                 = "ecs-it-tools-github-application"
  description          = "GitHub Actions image publishing for ecs-it-tools"
  assume_role_policy   = data.aws_iam_policy_document.github_dev_trust.json
  max_session_duration = 3600

  tags = {
    Project = "ecs-it-tools"
    Purpose = "GitHub Actions application image publishing"
  }
}

data "aws_iam_policy_document" "github_application" {
  statement {
    sid       = "RegistryAuthentication"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "PublishAndVerifyApplicationImages"
    effect = "Allow"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeImages",
      "ecr:DescribeRepositories",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]

    resources = [
      "arn:aws:ecr:eu-west-2:670941257756:repository/ecs-it-tools"
    ]
  }
}

resource "aws_iam_role_policy" "github_application" {
  name   = "ecs-it-tools-image-publishing"
  role   = aws_iam_role.github_application.id
  policy = data.aws_iam_policy_document.github_application.json
}

output "github_application_role_arn" {
  value = aws_iam_role.github_application.arn
}