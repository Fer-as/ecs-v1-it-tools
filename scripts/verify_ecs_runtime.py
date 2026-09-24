import json
import os
import subprocess


def aws(*args):
    return json.loads(subprocess.check_output(
        ["aws", *args, "--region", "eu-west-2",
         "--output", "json", "--no-cli-pager"],
        text=True,
    ))


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    cluster = "ecs-it-tools-cluster"
    service_name = "ecs-it-tools-service"
    expected_image = (
        "670941257756.dkr.ecr.eu-west-2.amazonaws.com/ecs-it-tools:"
        + os.environ["TF_VAR_image_tag"]
    )
    expected_digest = os.environ["EXPECTED_IMAGE_DIGEST"]

    result = aws(
        "ecs", "describe-services",
        "--cluster", cluster, "--services", service_name,
    )
    require(not result.get("failures"), "ECS service lookup failed.")
    require(len(result["services"]) == 1, "Expected exactly one service.")
    service = result["services"][0]

    require(service["status"] == "ACTIVE", "Service is not ACTIVE.")
    require(
        (service["desiredCount"], service["runningCount"],
         service["pendingCount"]) == (1, 1, 0),
        "Expected one desired/running task and zero pending tasks.",
    )
    deployments = service["deployments"]
    require(
        len(deployments) == 1
        and deployments[0]["status"] == "PRIMARY"
        and deployments[0].get("rolloutState") == "COMPLETED"
        and deployments[0].get("failedTasks", 0) == 0,
        "Service deployment is not successfully completed.",
    )
    require(
        service["networkConfiguration"]["awsvpcConfiguration"]
        ["assignPublicIp"] == "DISABLED",
        "Service public IP assignment must be disabled.",
    )

    task_arns = aws(
        "ecs", "list-tasks", "--cluster", cluster,
        "--service-name", service_name, "--desired-status", "RUNNING",
    )["taskArns"]
    require(len(task_arns) == 1, "Expected exactly one running service task.")

    result = aws(
        "ecs", "describe-tasks", "--cluster", cluster,
        "--tasks", task_arns[0],
    )
    require(not result.get("failures"), "Task lookup failed.")
    require(len(result["tasks"]) == 1, "Expected exactly one task.")
    task = result["tasks"][0]
    require(task["lastStatus"] == "RUNNING", "Task is not RUNNING.")
    require(
        task["taskDefinitionArn"] == service["taskDefinition"],
        "Running task does not use the service's selected task definition.",
    )

    definition = aws(
        "ecs", "describe-task-definition",
        "--task-definition", task["taskDefinitionArn"],
    )["taskDefinition"]
    require(
        definition["runtimePlatform"]["cpuArchitecture"] == "X86_64"
        and definition["runtimePlatform"]["operatingSystemFamily"] == "LINUX",
        "Unexpected task platform.",
    )

    containers = [
        item for item in task["containers"]
        if item["name"] == "ecs-it-tools"
    ]
    require(len(containers) == 1, "Application container missing or ambiguous.")
    container = containers[0]
    require(container["lastStatus"] == "RUNNING", "Container is not RUNNING.")
    require(container["image"] == expected_image, "Running image tag mismatch.")
    require(
        container.get("imageDigest") == expected_digest,
        "Running digest differs from the supplied ECR digest. "
        "Inspect index/platform-manifest identity before proceeding.",
    )

    interfaces = container["networkInterfaces"]
    require(len(interfaces) == 1, "Expected one container network interface.")
    private_ip = interfaces[0]["privateIpv4Address"]

    eni_attachments = [
        item for item in task["attachments"]
        if item["type"] == "ElasticNetworkInterface"
    ]
    require(len(eni_attachments) == 1, "Expected one task ENI attachment.")
    details = {
        item["name"]: item["value"]
        for item in eni_attachments[0]["details"]
    }
    eni = aws(
        "ec2", "describe-network-interfaces",
        "--network-interface-ids", details["networkInterfaceId"],
    )["NetworkInterfaces"][0]
    require(
        not eni.get("Association", {}).get("PublicIp"),
        "Task ENI has a public IP.",
    )
    require(eni["PrivateIpAddress"] == private_ip, "Task ENI/IP mismatch.")

    load_balancers = service["loadBalancers"]
    require(len(load_balancers) == 1, "Expected one service target group.")
    target_group = load_balancers[0]["targetGroupArn"]
    targets = aws(
        "elbv2", "describe-target-health",
        "--target-group-arn", target_group,
    )["TargetHealthDescriptions"]
    matching_targets = [
        item for item in targets
        if item["Target"]["Id"] == private_ip
        and item["Target"]["Port"] == 8080
    ]
    require(
        len(matching_targets) == 1
        and matching_targets[0]["TargetHealth"]["State"] == "healthy",
        "Running task is not a healthy ALB target on port 8080.",
    )

    task_id = task["taskArn"].rsplit("/", 1)[1]
    log_stream = "ecs/ecs-it-tools/" + task_id
    events = aws(
        "logs", "get-log-events",
        "--log-group-name", "/ecs/ecs-it-tools",
        "--log-stream-name", log_stream,
        "--start-from-head", "--limit", "50",
    )["events"]
    require(len(events) > 0, "No logs returned for the running task.")

    print(json.dumps({
        "result": "PASS",
        "service": service_name,
        "deployment": deployments[0]["id"],
        "task": task["taskArn"],
        "task_definition": task["taskDefinitionArn"],
        "image": container["image"],
        "digest": container["imageDigest"],
        "platform": "LINUX/X86_64",
        "private_ip": private_ip,
        "public_ip": None,
        "target_group": target_group,
        "target_health": "healthy",
        "log_stream": log_stream,
        "log_events_retrieved": len(events),
    }, indent=2))


if __name__ == "__main__":
    main()