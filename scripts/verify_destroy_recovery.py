"""Check the original destroy plan against current resources after verifier failure."""
import json
import os
from pathlib import Path
import re
import sys
from zipfile import ZipFile

from check_destroy_plan import check_plan, require
from verify_destroy_cleanup import DNS_REMOVED, protected_records, verify

ORIGINAL_RUN = 36269051826
ORIGINAL_COMMIT = "119d285b15ba4ec4f4dfd5f8d12d90cf5c4d9ecc"
ORIGINAL_STATE_VERSION = "ajD_Rkcm8F_oXKif_JcdDmuW7oBPM80v"
ORIGINAL_ECR_IMAGES = 1
ORIGINAL_NAT = "nat-00d4f978d139944b2"
ORIGINAL_EIP = "eipalloc-04b6bdd1421211d2b"
DNS_LOG = "plan/8_Inspect DNS before planning.txt"
PREAPPLY_LOG = "apply/8_Recheck approved destroy scope and capture retained resources.txt"
TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\S+Z ")


def original_dns_records(log_archive):
    with ZipFile(log_archive) as archive:
        matches = [name for name in archive.namelist() if name.endswith(DNS_LOG)]
        require(len(matches) == 1, "Original DNS inspection log missing or ambiguous")
        lines = archive.read(matches[0]).decode("utf-8").splitlines()
    output = "\n".join(TIMESTAMP.sub("", line) for line in lines)
    decoder = json.JSONDecoder()
    for match in re.finditer(r"(?m)^\{\s*$", output):
        try:
            value, _ = decoder.raw_decode(output[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get("ResourceRecordSets"), list):
            records = value["ResourceRecordSets"]
            present = {(item["Name"].rstrip("."), item["Type"]) for item in records}
            require(DNS_REMOVED <= present, "Original DNS inventory lacks application records")
            return records
    raise SystemExit("No Route53 record-set JSON in original run log")


def original_preapply_baseline(log_archive):
    with ZipFile(log_archive) as archive:
        matches = [name for name in archive.namelist() if name.endswith(PREAPPLY_LOG)]
        require(len(matches) == 1, "Original pre-apply capture log missing or ambiguous")
        lines = archive.read(matches[0]).decode("utf-8").splitlines()
    captures = []
    for line in lines:
        line = TIMESTAMP.sub("", line)
        if line.startswith('{"state_before":'):
            captures.append(json.loads(line))
    require(len(captures) == 1, "Original pre-apply state capture missing or ambiguous")
    capture = captures[0]
    require(capture.get("state_before") == {
        "VersionId": ORIGINAL_STATE_VERSION, "ServerSideEncryption": "AES256"},
        "Original pre-apply state metadata mismatch")
    require(capture.get("ecr_images_before_apply") == ORIGINAL_ECR_IMAGES,
            "Original pre-apply ECR image count mismatch")
    return capture


def check_original_plan(plan):
    require(os.environ.get("TF_VAR_image_tag") == ORIGINAL_COMMIT,
            "Recovery image input does not match the original run")
    changes = check_plan(plan, ORIGINAL_COMMIT)
    require(len(changes) == 33, "Original plan does not contain 33 deletes")
    by_address = {item["address"]: item["change"]["before"] for item in changes}
    require(by_address["module.vpc.aws_nat_gateway.this"]["id"] == ORIGINAL_NAT,
            "Original NAT identity mismatch")
    require(by_address["module.vpc.aws_eip.nat"]["id"] == ORIGINAL_EIP,
            "Original EIP identity mismatch")
    require("module.ecr.aws_ecr_repository.this" in by_address,
            "Original ECR repository missing from plan")
    return changes


def main(plan_path, log_archive):
    with Path(plan_path).open(encoding="utf-8") as stream:
        plan = json.load(stream)
    changes = check_original_plan(plan)
    dns_before = original_dns_records(log_archive)
    original_preapply_baseline(log_archive)
    baseline = {
        "protected_dns": protected_records(dns_before),
        "state": {"VersionId": ORIGINAL_STATE_VERSION},
        "ecr_image_count": ORIGINAL_ECR_IMAGES,
    }
    print(json.dumps({
        "original_run": ORIGINAL_RUN,
        "original_workflow_commit": ORIGINAL_COMMIT,
        "approved_plan_deletes": len(changes),
        "dns_baseline": "Original plan job: Inspect DNS before planning; not the lost pre-apply snapshot",
        "pre_apply_state_version": ORIGINAL_STATE_VERSION,
        "ecr_images_before_apply": ORIGINAL_ECR_IMAGES,
    }), flush=True)
    verify(plan, baseline)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Use PLAN_JSON ORIGINAL_RUN_LOG_ZIP")
    main(sys.argv[1], sys.argv[2])
