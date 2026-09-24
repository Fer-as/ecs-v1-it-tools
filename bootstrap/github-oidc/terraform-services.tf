data "aws_iam_policy_document" "github_terraform_services" {
  statement {
    sid    = "ManageApplicationRepository"
    effect = "Allow"

    actions = [
      "ecr:CreateRepository",
      "ecr:DeleteRepository",
      "ecr:DescribeRepositories",
      "ecr:DescribeImages",
      "ecr:BatchGetImage",
      "ecr:ListTagsForResource",
      "ecr:PutImageScanningConfiguration",
      "ecr:PutImageTagMutability",
      "ecr:TagResource",
      "ecr:UntagResource",
    ]

    resources = [
      "arn:aws:ecr:eu-west-2:670941257756:repository/ecs-it-tools"
    ]
  }

  statement {
    sid    = "ManageApplicationCluster"
    effect = "Allow"

    actions = [
      "ecs:CreateCluster",
      "ecs:DeleteCluster",
      "ecs:DescribeClusters",
      "ecs:UpdateCluster",
      "ecs:UpdateClusterSettings",
    ]

    resources = [
      "arn:aws:ecs:eu-west-2:670941257756:cluster/ecs-it-tools-cluster"
    ]
  }

  statement {
    sid    = "ManageApplicationService"
    effect = "Allow"

    actions = [
      "ecs:CreateService",
      "ecs:DeleteService",
      "ecs:DescribeServices",
      "ecs:UpdateService",
    ]

    resources = [
      "arn:aws:ecs:eu-west-2:670941257756:service/ecs-it-tools-cluster/ecs-it-tools-service"
    ]
  }

  statement {
    sid     = "ListApplicationServiceDeployments"
    effect  = "Allow"
    actions = ["ecs:ListServiceDeployments"]

    resources = [
      "arn:aws:ecs:eu-west-2:670941257756:service/ecs-it-tools-cluster/ecs-it-tools-service"
    ]
  }

  statement {
    sid     = "DescribeApplicationServiceDeployments"
    effect  = "Allow"
    actions = ["ecs:DescribeServiceDeployments"]

    resources = [
      "arn:aws:ecs:eu-west-2:670941257756:service/ecs-it-tools-cluster/ecs-it-tools-service",
      "arn:aws:ecs:eu-west-2:670941257756:service-deployment/ecs-it-tools-cluster/ecs-it-tools-service/*",
    ]
  }

  statement {
    sid     = "ManageApplicationTaskDefinitions"
    effect  = "Allow"
    actions = ["ecs:RegisterTaskDefinition"]

    resources = [
      "arn:aws:ecs:eu-west-2:670941257756:task-definition/ecs-it-tools:*"
    ]
  }

  # DeregisterTaskDefinition does not support resource-level permissions.
  # This permits deregistration of any task definition in eu-west-2,
  # not only the application's family.
  statement {
    sid       = "DeregisterApplicationTaskDefinitions"
    effect    = "Allow"
    actions   = ["ecs:DeregisterTaskDefinition"]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = ["eu-west-2"]
    }
  }

  statement {
    sid    = "ManageApplicationEcsTags"
    effect = "Allow"

    actions = [
      "ecs:ListTagsForResource",
      "ecs:TagResource",
      "ecs:UntagResource",
    ]

    resources = [
      "arn:aws:ecs:eu-west-2:670941257756:cluster/ecs-it-tools-cluster",
      "arn:aws:ecs:eu-west-2:670941257756:service/ecs-it-tools-cluster/ecs-it-tools-service",
      "arn:aws:ecs:eu-west-2:670941257756:task-definition/ecs-it-tools:*",
    ]
  }

  statement {
    sid    = "ListApplicationTasks"
    effect = "Allow"

    actions   = ["ecs:ListTasks"]
    resources = ["*"]

    condition {
      test     = "ArnEquals"
      variable = "ecs:cluster"
      values = [
        "arn:aws:ecs:eu-west-2:670941257756:cluster/ecs-it-tools-cluster"
      ]
    }
  }

  statement {
    sid     = "InspectApplicationTasks"
    effect  = "Allow"
    actions = ["ecs:DescribeTasks"]

    resources = [
      "arn:aws:ecs:eu-west-2:670941257756:task/ecs-it-tools-cluster/*"
    ]
  }

  statement {
    sid    = "RegionalReadOperations"
    effect = "Allow"

    actions = [
      "ecs:DescribeTaskDefinition",
      "logs:DescribeLogGroups",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = ["eu-west-2"]
    }
  }

  statement {
    sid    = "ManageApplicationLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:DeleteLogGroup",
      "logs:PutRetentionPolicy",
      "logs:DeleteRetentionPolicy",
      "logs:DescribeLogStreams",
      "logs:GetLogEvents",
      "logs:FilterLogEvents",
      "logs:ListTagsForResource",
      "logs:ListTagsLogGroup",
      "logs:TagResource",
      "logs:UntagResource",
      "logs:TagLogGroup",
      "logs:UntagLogGroup",
    ]

    resources = [
      "arn:aws:logs:eu-west-2:670941257756:log-group:/ecs/ecs-it-tools",
      "arn:aws:logs:eu-west-2:670941257756:log-group:/ecs/ecs-it-tools:*",
    ]
  }
}

resource "aws_iam_role_policy" "github_terraform_services" {
  name   = "ecs-it-tools-terraform-services"
  role   = aws_iam_role.github_terraform.id
  policy = data.aws_iam_policy_document.github_terraform_services.json
}