data "aws_iam_policy_document" "github_terraform_acm" {
  statement {
    sid       = "RequestApplicationCertificate"
    effect    = "Allow"
    actions   = ["acm:RequestCertificate"]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestedRegion"
      values   = ["eu-west-2"]
    }

    condition {
      test     = "ForAllValues:StringEquals"
      variable = "acm:DomainNames"
      values   = ["tm.feras-dev.co.uk"]
    }

    condition {
      test     = "Null"
      variable = "acm:DomainNames"
      values   = ["false"]
    }

    condition {
      test     = "StringEquals"
      variable = "acm:ValidationMethod"
      values   = ["DNS"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/Name"
      values   = ["ecs-it-tools-certificate"]
    }
  }

  # RequestCertificate with tags also requires AddTagsToCertificate.
  # This allows assigning the specified Name tag to certificates in
  # this account/region; it is not an immutable ownership boundary.
  statement {
    sid     = "SetApplicationCertificateTag"
    effect  = "Allow"
    actions = ["acm:AddTagsToCertificate"]

    resources = [
      "arn:aws:acm:eu-west-2:670941257756:certificate/*"
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:RequestTag/Name"
      values   = ["ecs-it-tools-certificate"]
    }

    condition {
      test     = "ForAllValues:StringEquals"
      variable = "aws:TagKeys"
      values   = ["Name"]
    }
  }

  statement {
    sid    = "InspectRegionalCertificates"
    effect = "Allow"

    actions = [
      "acm:DescribeCertificate",
      "acm:ListTagsForCertificate",
    ]

    resources = [
      "arn:aws:acm:eu-west-2:670941257756:certificate/*"
    ]
  }

  statement {
    sid    = "ManageTaggedApplicationCertificates"
    effect = "Allow"

    actions = [
      "acm:DeleteCertificate",
      "acm:UpdateCertificateOptions",
    ]

    resources = [
      "arn:aws:acm:eu-west-2:670941257756:certificate/*"
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Name"
      values   = ["ecs-it-tools-certificate"]
    }
  }
}

resource "aws_iam_role_policy" "github_terraform_acm" {
  name   = "ecs-it-tools-terraform-acm"
  role   = aws_iam_role.github_terraform.id
  policy = data.aws_iam_policy_document.github_terraform_acm.json
}