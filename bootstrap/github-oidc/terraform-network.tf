data "aws_iam_policy_document" "github_terraform_network" {
  statement {
    sid    = "InspectRegionalNetworking"
    effect = "Allow"

    actions = [
      "ec2:DescribeAddresses",
      "ec2:DescribeAddressesAttribute",
      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeInternetGateways",
      "ec2:DescribeNatGateways",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSecurityGroupRules",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeTags",
      "ec2:DescribeVpcAttribute",
      "ec2:DescribeVpcs",
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = ["eu-west-2"]
    }
  }

  # These permissions are account/region scoped, not project scoped.
  # Untagged resources and generated IDs must survive recreation.
  statement {
    sid    = "ManageRegionalNetworkResources"
    effect = "Allow"

    actions = [
      "ec2:AllocateAddress",
      "ec2:ReleaseAddress",
      "ec2:CreateVpc",
      "ec2:DeleteVpc",
      "ec2:ModifyVpcAttribute",
      "ec2:CreateSubnet",
      "ec2:DeleteSubnet",
      "ec2:ModifySubnetAttribute",
      "ec2:CreateInternetGateway",
      "ec2:DeleteInternetGateway",
      "ec2:AttachInternetGateway",
      "ec2:DetachInternetGateway",
      "ec2:CreateNatGateway",
      "ec2:DeleteNatGateway",
      "ec2:CreateRouteTable",
      "ec2:DeleteRouteTable",
      "ec2:AssociateRouteTable",
      "ec2:DisassociateRouteTable",
      "ec2:ReplaceRouteTableAssociation",
      "ec2:CreateRoute",
      "ec2:DeleteRoute",
      "ec2:ReplaceRoute",
      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:RevokeSecurityGroupEgress",
      "ec2:ModifySecurityGroupRules",
      "ec2:UpdateSecurityGroupRuleDescriptionsIngress",
      "ec2:UpdateSecurityGroupRuleDescriptionsEgress",
      "ec2:CreateTags",
      "ec2:DeleteTags",
    ]

    resources = [
      "arn:aws:ec2:eu-west-2:670941257756:elastic-ip/*",
      "arn:aws:ec2:eu-west-2:670941257756:internet-gateway/*",
      "arn:aws:ec2:eu-west-2:670941257756:natgateway/*",
      "arn:aws:ec2:eu-west-2:670941257756:route-table/*",
      "arn:aws:ec2:eu-west-2:670941257756:security-group/*",
      "arn:aws:ec2:eu-west-2:670941257756:security-group-rule/*",
      "arn:aws:ec2:eu-west-2:670941257756:subnet/*",
      "arn:aws:ec2:eu-west-2:670941257756:vpc/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = ["eu-west-2"]
    }
  }
}

resource "aws_iam_policy" "github_terraform_network" {
  name        = "ecs-it-tools-terraform-network"
  description = "Regional networking permissions for application Terraform"
  policy      = data.aws_iam_policy_document.github_terraform_network.json

  tags = {
    Project = "ecs-it-tools"
    Purpose = "GitHub Actions Terraform networking"
  }
}

resource "aws_iam_role_policy_attachment" "github_terraform_network" {
  role       = aws_iam_role.github_terraform.name
  policy_arn = aws_iam_policy.github_terraform_network.arn
}