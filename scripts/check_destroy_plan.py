"""Fail closed on anything outside this application's destroy inventory."""
import json
import os
import re
import sys

ACCOUNT = "670941257756"
REGION = "eu-west-2"
ZONE = "Z01014153ETFBQT2QXXK2"
APP_RECORD = "tm.feras-dev.co.uk"
VALIDATION_RECORD = "_acc09de86e15890a1ed86e2e77a7c5dc.tm.feras-dev.co.uk"

# Explicit instance addresses: a new resource requires a reviewed guard update.
ADDRESSES = {
    "aws_acm_certificate.this",
    "aws_acm_certificate_validation.this",
    "aws_route53_record.app",
    'aws_route53_record.certificate_validation["tm.feras-dev.co.uk"]',
    "module.alb.aws_lb.this",
    "module.alb.aws_lb_listener.http",
    "module.alb.aws_lb_listener.https",
    "module.alb.aws_lb_target_group.this",
    "module.alb.aws_security_group.alb",
    "module.ecr.aws_ecr_repository.this",
    "module.ecs.aws_cloudwatch_log_group.this",
    "module.ecs.aws_ecs_cluster.this",
    "module.ecs.aws_ecs_service.this",
    "module.ecs.aws_ecs_task_definition.this",
    "module.ecs.aws_iam_role.execution",
    "module.ecs.aws_iam_role_policy_attachment.execution",
    "module.ecs.aws_security_group.task",
    "module.ecs.aws_vpc_security_group_egress_rule.task_outbound",
    "module.ecs.aws_vpc_security_group_ingress_rule.alb_to_task",
    "module.vpc.aws_eip.nat",
    "module.vpc.aws_internet_gateway.this",
    "module.vpc.aws_nat_gateway.this",
    "module.vpc.aws_route_table.private",
    "module.vpc.aws_route_table.public",
} | {
    f"module.vpc.{kind}.{side}[{index}]"
    for kind in ("aws_subnet", "aws_route_table_association")
    for side in ("public", "private")
    for index in (0, 1)
} | {"module.vpc.aws_vpc.this"}


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def resources(module):
    yield from module.get("resources", [])
    for child in module.get("child_modules", []):
        yield from resources(child)


def check_identity(item):
    address = item["address"]
    require(address in ADDRESSES, "Unapproved address: " + address)
    expected_type = re.search(r"(?:^|\.)(aws_[^.]+)\.", address).group(1)
    require(item["type"] == expected_type, "Resource type mismatch: " + address)
    before = item["change"]["before"]
    require(isinstance(before, dict), "Missing prior values: " + address)
    arn = before.get("arn")
    if arn:
        parts = arn.split(":", 5)
        require(len(parts) == 6 and parts[0:2] == ["arn", "aws"], "Invalid ARN")
        require(parts[4] == ACCOUNT, "Unexpected resource account: " + address)
        require(parts[3] in (REGION, ""), "Unexpected resource region: " + address)

    fixed = {
        "module.ecr.aws_ecr_repository.this": ("name", "ecs-it-tools"),
        "module.ecs.aws_ecs_cluster.this": ("name", "ecs-it-tools-cluster"),
        "module.ecs.aws_ecs_service.this": ("name", "ecs-it-tools-service"),
        "module.ecs.aws_ecs_task_definition.this": ("family", "ecs-it-tools"),
        "module.ecs.aws_iam_role.execution": ("name", "ecs-it-tools-ecs-execution"),
        "module.ecs.aws_cloudwatch_log_group.this": ("name", "/ecs/ecs-it-tools"),
        "module.alb.aws_lb.this": ("name", "ecs-it-tools-alb"),
        "module.alb.aws_lb_target_group.this": ("name", "ecs-it-tools-tg"),
        "module.alb.aws_security_group.alb": ("name", "ecs-it-tools-alb-sg"),
        "module.ecs.aws_security_group.task": ("name", "ecs-it-tools-ecs-task-sg"),
        "aws_acm_certificate.this": ("domain_name", APP_RECORD),
    }
    if address in fixed:
        key, value = fixed[address]
        require(before.get(key) == value, "Unexpected resource identity: " + address)
    if item["type"] == "aws_route53_record":
        name, kind = ((APP_RECORD, "A") if address == "aws_route53_record.app"
                      else (VALIDATION_RECORD, "CNAME"))
        require(before.get("zone_id") == ZONE
                and before.get("name", "").rstrip(".") == name
                and before.get("type") == kind, "Unexpected DNS record: " + address)
    if item["type"] == "aws_iam_role_policy_attachment":
        require(before.get("role") == "ecs-it-tools-ecs-execution"
                and before.get("policy_arn") ==
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
                "Unexpected role attachment")
    if item["type"] == "aws_ecr_repository":
        require(before.get("force_delete") is True, "ECR force_delete must be enabled")


def check_plan(plan, image_tag):
    require(re.fullmatch(r"[0-9a-f]{40}", image_tag) is not None, "Invalid image SHA")
    require(not plan.get("errored") and not plan.get("deferred_changes"),
            "Errored or deferred destroy plan")
    expected = {"image_tag": image_tag, "aws_region": REGION,
                "hosted_zone_id": ZONE, "project_name": "ecs-it-tools",
                "domain_name": "feras-dev.co.uk", "subdomain_name": "tm"}
    for name, value in expected.items():
        require(plan.get("variables", {}).get(name, {}).get("value") == value,
                "Plan variable mismatch: " + name)
    require(not any(r.get("mode") == "managed" for r in resources(
        plan.get("planned_values", {}).get("root_module", {}))),
        "Destroy plan must leave no managed resources")
    for drift in plan.get("resource_drift", []):
        if drift.get("mode") == "managed":
            require(drift["address"] in ADDRESSES, "Unexpected drift address")
    changes = []
    for item in plan.get("resource_changes", []):
        if item["mode"] != "managed":
            continue
        require(not item["change"].get("importing"), "Imports are prohibited")
        require(not item.get("previous_address"), "Resource moves are prohibited")
        require(not item.get("deposed"), "Deposed instances require separate review")
        require(item["change"]["actions"] == ["delete"],
                "Only deletes are allowed: " + item["address"])
        check_identity(item)
        changes.append(item)
    require(len({r["address"] for r in changes}) == len(changes), "Duplicate addresses")
    return changes


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as stream:
        changes = check_plan(json.load(stream), os.environ["TF_VAR_image_tag"])
    for item in changes:
        print(item["address"], "delete")
    print(f"Destroy scope PASS: {len(changes)} deletes; no creates or updates.")
    print("Operator review required. ECR images and application logs will be deleted.")
