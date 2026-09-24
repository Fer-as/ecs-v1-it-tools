data "aws_iam_policy_document" "github_terraform_dns" {
  statement {
    sid    = "InspectRetainedHostedZone"
    effect = "Allow"

    actions = [
      "route53:GetHostedZone",
      "route53:ListResourceRecordSets",
      "route53:ListTagsForResource",
    ]

    resources = [
      "arn:aws:route53:::hostedzone/Z01014153ETFBQT2QXXK2"
    ]
  }

  statement {
    sid       = "WaitForDnsChanges"
    effect    = "Allow"
    actions   = ["route53:GetChange"]
    resources = ["arn:aws:route53:::change/*"]
  }

  statement {
    sid     = "ManageApplicationAlias"
    effect  = "Allow"
    actions = ["route53:ChangeResourceRecordSets"]

    resources = [
      "arn:aws:route53:::hostedzone/Z01014153ETFBQT2QXXK2"
    ]

    condition {
      test     = "ForAllValues:StringEquals"
      variable = "route53:ChangeResourceRecordSetsNormalizedRecordNames"
      values   = ["tm.feras-dev.co.uk"]
    }

    condition {
      test     = "ForAllValues:StringEquals"
      variable = "route53:ChangeResourceRecordSetsRecordTypes"
      values   = ["A"]
    }
  }

  statement {
    sid     = "ManageCertificateValidationRecord"
    effect  = "Allow"
    actions = ["route53:ChangeResourceRecordSets"]

    resources = [
      "arn:aws:route53:::hostedzone/Z01014153ETFBQT2QXXK2"
    ]

    condition {
      test     = "ForAllValues:StringEquals"
      variable = "route53:ChangeResourceRecordSetsNormalizedRecordNames"
      values = [
        "_acc09de86e15890a1ed86e2e77a7c5dc.tm.feras-dev.co.uk"
      ]
    }

    condition {
      test     = "ForAllValues:StringEquals"
      variable = "route53:ChangeResourceRecordSetsRecordTypes"
      values   = ["CNAME"]
    }
  }
}

resource "aws_iam_role_policy" "github_terraform_dns" {
  name   = "ecs-it-tools-terraform-dns"
  role   = aws_iam_role.github_terraform.id
  policy = data.aws_iam_policy_document.github_terraform_dns.json
}