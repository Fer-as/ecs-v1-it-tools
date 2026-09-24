data "aws_iam_policy_document" "github_terraform_alb" {
  statement {
    sid    = "InspectRegionalLoadBalancing"
    effect = "Allow"

    actions = [
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:DescribeLoadBalancerAttributes",
      "elasticloadbalancing:DescribeListeners",
      "elasticloadbalancing:DescribeListenerAttributes",
      "elasticloadbalancing:DescribeListenerCertificates",
      "elasticloadbalancing:DescribeTargetGroups",
      "elasticloadbalancing:DescribeTargetGroupAttributes",
      "elasticloadbalancing:DescribeTargetHealth",
      "elasticloadbalancing:DescribeTags",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = ["eu-west-2"]
    }
  }

  statement {
    sid    = "ManageApplicationLoadBalancer"
    effect = "Allow"

    actions = [
      "elasticloadbalancing:CreateLoadBalancer",
      "elasticloadbalancing:DeleteLoadBalancer",
      "elasticloadbalancing:ModifyLoadBalancerAttributes",
      "elasticloadbalancing:SetSecurityGroups",
      "elasticloadbalancing:SetSubnets",
      "elasticloadbalancing:SetIpAddressType",
    ]

    resources = [
      "arn:aws:elasticloadbalancing:eu-west-2:670941257756:loadbalancer/app/ecs-it-tools-alb/*"
    ]
  }

  statement {
    sid     = "CreateApplicationListeners"
    effect  = "Allow"
    actions = ["elasticloadbalancing:CreateListener"]

    resources = [
      "arn:aws:elasticloadbalancing:eu-west-2:670941257756:loadbalancer/app/ecs-it-tools-alb/*"
    ]
  }

  statement {
    sid    = "ManageApplicationListeners"
    effect = "Allow"

    actions = [
      "elasticloadbalancing:DeleteListener",
      "elasticloadbalancing:ModifyListener",
      "elasticloadbalancing:ModifyListenerAttributes",
    ]

    resources = [
      "arn:aws:elasticloadbalancing:eu-west-2:670941257756:listener/app/ecs-it-tools-alb/*/*"
    ]
  }

  statement {
    sid    = "ManageApplicationTargetGroup"
    effect = "Allow"

    actions = [
      "elasticloadbalancing:CreateTargetGroup",
      "elasticloadbalancing:DeleteTargetGroup",
      "elasticloadbalancing:ModifyTargetGroup",
      "elasticloadbalancing:ModifyTargetGroupAttributes",
    ]

    resources = [
      "arn:aws:elasticloadbalancing:eu-west-2:670941257756:targetgroup/ecs-it-tools-tg/*"
    ]
  }

  statement {
    sid    = "ManageApplicationLoadBalancingTags"
    effect = "Allow"

    actions = [
      "elasticloadbalancing:AddTags",
      "elasticloadbalancing:RemoveTags",
    ]

    resources = [
      "arn:aws:elasticloadbalancing:eu-west-2:670941257756:loadbalancer/app/ecs-it-tools-alb/*",
      "arn:aws:elasticloadbalancing:eu-west-2:670941257756:listener/app/ecs-it-tools-alb/*/*",
      "arn:aws:elasticloadbalancing:eu-west-2:670941257756:targetgroup/ecs-it-tools-tg/*",
    ]
  }
}

resource "aws_iam_role_policy" "github_terraform_alb" {
  name   = "ecs-it-tools-terraform-alb"
  role   = aws_iam_role.github_terraform.id
  policy = data.aws_iam_policy_document.github_terraform_alb.json
}