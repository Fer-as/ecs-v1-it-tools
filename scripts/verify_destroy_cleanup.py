"""Read-only cleanup probes. API errors never count as successful absence."""
import json
import os
import re
import subprocess
import sys
import time

from check_destroy_plan import APP_RECORD, VALIDATION_RECORD, ZONE, check_plan, require

BUCKET = "feras-ecs-it-tools-tfstate-670941257756"
STATE_KEY = "ecs-v1/dev/terraform.tfstate"
DNS_REMOVED = {(APP_RECORD, "A"), (VALIDATION_RECORD, "CNAME")}


def aws(*args, absent_codes=(), absent_messages=()):
    result = subprocess.run(
        ["aws", *args, "--region", "eu-west-2", "--output", "json",
         "--no-cli-pager", "--cli-connect-timeout", "10", "--cli-read-timeout", "30"],
        capture_output=True, text=True, timeout=90,
    )
    if result.returncode:
        match = re.search(r"An error occurred \(([^)]+)\)", result.stderr)
        if match and match.group(1) in absent_codes:
            return None
        if match:
            message = result.stderr.strip().split(" operation: ", 1)[-1]
            if (match.group(1), message) in absent_messages:
                return None
        raise SystemExit("AWS inspection failed: " + result.stderr.strip())
    return json.loads(result.stdout)


def dns_records():
    return aws("route53", "list-resource-record-sets", "--hosted-zone-id", ZONE)[
        "ResourceRecordSets"]


def protected_records(records):
    return sorted(
        json.dumps(r, sort_keys=True) for r in records
        if (r["Name"].rstrip("."), r["Type"]) not in DNS_REMOVED
    )


def state_metadata():
    result = aws("s3api", "head-object", "--bucket", BUCKET, "--key", STATE_KEY)
    require(result.get("VersionId") not in (None, "", "null"),
            "State object has no version ID")
    require(result.get("ServerSideEncryption") in ("AES256", "aws:kms"),
            "State object is not server-side encrypted")
    return {key: result[key] for key in ("VersionId", "ServerSideEncryption")}


def snapshot():
    zone = aws("route53", "get-hosted-zone", "--id", ZONE)["HostedZone"]
    require(zone["Name"] == "feras-dev.co.uk." and not zone["Config"]["PrivateZone"],
            "Unexpected retained hosted zone")
    images = aws("ecr", "describe-images", "--repository-name", "ecs-it-tools",
                 absent_codes=("RepositoryNotFoundException",))
    return {
        "protected_dns": protected_records(dns_records()),
        "state": state_metadata(),
        "ecr_image_count": len(images["imageDetails"]) if images else 0,
    }


def removed(item):
    kind = item["type"]
    v = item["change"]["before"]
    # EC2 filters return empty lists for absent resources, without broad error handling.
    ec2 = {
        "aws_vpc": ("describe-vpcs", "vpc-id", "Vpcs"),
        "aws_subnet": ("describe-subnets", "subnet-id", "Subnets"),
        "aws_internet_gateway": ("describe-internet-gateways", "internet-gateway-id", "InternetGateways"),
        "aws_eip": ("describe-addresses", "allocation-id", "Addresses"),
        "aws_nat_gateway": ("describe-nat-gateways", "nat-gateway-id", "NatGateways"),
        "aws_route_table": ("describe-route-tables", "route-table-id", "RouteTables"),
        "aws_route_table_association": ("describe-route-tables", "association.route-table-association-id", "RouteTables"),
        "aws_security_group": ("describe-security-groups", "group-id", "SecurityGroups"),
    }
    if kind in ec2:
        operation, field, key = ec2[kind]
        filter_option = "--filter" if kind == "aws_nat_gateway" else "--filters"
        rows = aws("ec2", operation, filter_option, f"Name={field},Values={v['id']}")[key]
        if kind == "aws_nat_gateway":
            return all(r["State"] == "deleted" for r in rows)
        return not rows
    if kind in ("aws_vpc_security_group_ingress_rule", "aws_vpc_security_group_egress_rule"):
        result = aws("ec2", "describe-security-group-rules", "--filters",
                     f"Name=security-group-rule-id,Values={v['id']}")
        return not result["SecurityGroupRules"]
    if kind == "aws_ecr_repository":
        return aws("ecr", "describe-repositories", "--repository-names", v["name"],
                   absent_codes=("RepositoryNotFoundException",)) is None
    if kind == "aws_ecs_cluster":
        result = aws("ecs", "describe-clusters", "--clusters", v["arn"])
        require(all(f.get("reason") == "MISSING" for f in result.get("failures", [])),
                "Unexpected ECS cluster lookup failure")
        return all(r["status"] == "INACTIVE" and r.get("runningTasksCount", 0) == 0
                   and r.get("pendingTasksCount", 0) == 0
                   and r.get("activeServicesCount", 0) == 0 for r in result["clusters"])
    if kind == "aws_ecs_service":
        result = aws("ecs", "describe-services", "--cluster", v["cluster"],
                     "--services", v["name"], absent_codes=("ClusterNotFoundException", "ServiceNotFoundException"))
        if result is None:
            return True
        require(all(f.get("reason") == "MISSING" for f in result.get("failures", [])),
                "Unexpected ECS service lookup failure")
        return all(r["status"] == "INACTIVE" and r["runningCount"] == 0
                   and r["pendingCount"] == 0 for r in result["services"])
    if kind == "aws_ecs_task_definition":
        # Terraform deregisters task definitions; it does not erase revision history.
        result = aws(
            "ecs", "describe-task-definition", "--task-definition", v["arn"],
            absent_messages=(("ClientException", "Unable to describe task definition."),),
        )
        return result is None or result["taskDefinition"]["status"] == "INACTIVE"
    if kind == "aws_cloudwatch_log_group":
        rows = aws("logs", "describe-log-groups", "--log-group-name-prefix", v["name"])["logGroups"]
        return not any(r["logGroupName"] == v["name"] for r in rows)
    if kind == "aws_iam_role":
        return aws("iam", "get-role", "--role-name", v["name"],
                   absent_codes=("NoSuchEntity",)) is None
    if kind == "aws_iam_role_policy_attachment":
        result = aws("iam", "list-attached-role-policies", "--role-name", v["role"],
                     absent_codes=("NoSuchEntity",))
        return result is None or not any(
            r["PolicyArn"] == v["policy_arn"] for r in result["AttachedPolicies"])
    elb = {
        "aws_lb": ("describe-load-balancers", "--load-balancer-arns", "LoadBalancerNotFound"),
        "aws_lb_listener": ("describe-listeners", "--listener-arns", "ListenerNotFound"),
        "aws_lb_target_group": ("describe-target-groups", "--target-group-arns", "TargetGroupNotFound"),
    }
    if kind in elb:
        operation, option, code = elb[kind]
        return aws("elbv2", operation, option, v["arn"], absent_codes=(code,)) is None
    if kind in ("aws_acm_certificate", "aws_acm_certificate_validation"):
        # Validation is a Terraform waiter, so inspect its actual certificate.
        arn = v["arn"] if kind == "aws_acm_certificate" else v["certificate_arn"]
        return aws("acm", "describe-certificate", "--certificate-arn", arn,
                   absent_codes=("ResourceNotFoundException",)) is None
    if kind == "aws_route53_record":
        return not any(r["Name"].rstrip(".") == v["name"].rstrip(".")
                       and r["Type"] == v["type"] for r in dns_records())
    raise SystemExit("No cleanup probe for " + kind)


def verify(plan, before):
    changes = check_plan(plan, os.environ["TF_VAR_image_tag"])
    pending = changes[:]
    for attempt in range(1, 13):
        pending = [item for item in pending if not removed(item)]
        print(json.dumps({"check": "cleanup", "attempt": attempt,
                          "remaining": [r["address"] for r in pending]}), flush=True)
        if not pending:
            break
        if attempt < 12:
            time.sleep(10)
    require(not pending, "AWS resources remain after destroy")

    state = json.loads(subprocess.check_output(
        ["terraform", "-chdir=terraform", "state", "pull"], text=True, timeout=90))
    require(not any(r.get("mode") == "managed" and r.get("instances")
                    for r in state.get("resources", [])), "Managed resources remain in state")
    records = dns_records()
    require(not any((r["Name"].rstrip("."), r["Type"]) in DNS_REMOVED for r in records),
            "Application DNS records remain")
    require(protected_records(records) == before["protected_dns"],
            "Retained DNS records changed during destroy")
    zone = aws("route53", "get-hosted-zone", "--id", ZONE)["HostedZone"]
    require(zone["Name"] == "feras-dev.co.uk." and not zone["Config"]["PrivateZone"],
            "Retained hosted zone mismatch")
    after = state_metadata()
    if changes:
        require(after["VersionId"] != before["state"]["VersionId"],
                "State object version did not change after destroy")
    print(json.dumps({
        "result": "PASS", "planned_resources_checked": len(changes),
        "managed_state_empty": True, "application_dns_removed": True,
        "retained_dns_unchanged": True, "backend_state": after,
        "ecr_images_before_apply": before["ecr_image_count"],
        "task_definition_history": "Deregistered revisions may remain INACTIVE",
        "scope": "Approved plan resources; not an account-wide orphan audit",
    }, indent=2))


if __name__ == "__main__":
    if sys.argv[1] == "capture":
        baseline = snapshot()
        with open(sys.argv[2], "w", encoding="utf-8") as stream:
            json.dump(baseline, stream)
        print(json.dumps({"state_before": baseline["state"],
                          "ecr_images_before_apply": baseline["ecr_image_count"]}))
    elif sys.argv[1] == "verify":
        with open(sys.argv[2], encoding="utf-8") as stream:
            plan = json.load(stream)
        with open(sys.argv[3], encoding="utf-8") as stream:
            baseline = json.load(stream)
        verify(plan, baseline)
    else:
        raise SystemExit("Use capture BASELINE or verify PLAN BASELINE")
