"""Offline tests: no AWS credentials or calls required."""
import copy
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_destroy_plan as guard
import verify_destroy_cleanup as cleanup
import verify_destroy_recovery as recovery

SHA = "b2da1c81729398b7e792b97401f7fadde64471a9"


def plan_fixture():
    return {
        "variables": {k: {"value": v} for k, v in {
            "image_tag": SHA, "aws_region": guard.REGION, "hosted_zone_id": guard.ZONE,
            "project_name": "ecs-it-tools", "domain_name": "feras-dev.co.uk",
            "subdomain_name": "tm",
        }.items()},
        "planned_values": {"root_module": {}},
        "resource_changes": [{
            "address": "module.ecr.aws_ecr_repository.this", "mode": "managed",
            "type": "aws_ecr_repository", "change": {"actions": ["delete"], "before": {
                "name": "ecs-it-tools", "force_delete": True,
                "arn": "arn:aws:ecr:eu-west-2:670941257756:repository/ecs-it-tools",
            }},
        }],
    }


class GuardTests(unittest.TestCase):
    def test_known_delete_and_empty_recovery(self):
        p = plan_fixture()
        self.assertEqual(len(guard.check_plan(p, SHA)), 1)
        p["resource_changes"] = []
        self.assertEqual(guard.check_plan(p, SHA), [])
        self.assertEqual(len(guard.ADDRESSES), 33)

    def test_invalid_plans_rejected(self):
        def modify_change(p, key, value):
            p["resource_changes"][0]["change"][key] = value
        cases = [
            lambda p: modify_change(p, "actions", ["create"]),
            lambda p: modify_change(p, "actions", ["update"]),
            lambda p: modify_change(p, "actions", ["delete", "create"]),
            lambda p: modify_change(p, "actions", ["no-op"]),
            lambda p: modify_change(p, "importing", {"id": "external"}),
            lambda p: p.update(errored=True),
            lambda p: p.update(deferred_changes=[{}]),
            lambda p: p["resource_changes"][0].update(address="aws_s3_bucket.backend"),
            lambda p: p["resource_changes"][0].update(type="aws_iam_role"),
            lambda p: p["resource_changes"][0].update(previous_address="old"),
            lambda p: p["resource_changes"][0].update(deposed="1234"),
            lambda p: p["resource_changes"].append(copy.deepcopy(p["resource_changes"][0])),
            lambda p: p["resource_changes"][0]["change"]["before"].update(name="other"),
            lambda p: p["resource_changes"][0]["change"]["before"].update(force_delete=False),
            lambda p: p["resource_changes"][0]["change"]["before"].update(
                arn="arn:aws:ecr:eu-west-2:000000000000:repository/ecs-it-tools"),
            lambda p: p["variables"]["hosted_zone_id"].update(value="OTHER"),
            lambda p: p["planned_values"]["root_module"].update(child_modules=[{
                "resources": [{"mode": "managed"}]}]),
        ]
        for index, change in enumerate(cases):
            with self.subTest(case=index):
                p = plan_fixture()
                change(p)
                with self.assertRaises(SystemExit):
                    guard.check_plan(p, SHA)

    def test_validation_record_address_and_zone(self):
        p = plan_fixture()
        p["resource_changes"] = [{
            "address": 'aws_route53_record.certificate_validation["tm.feras-dev.co.uk"]',
            "mode": "managed", "type": "aws_route53_record", "change": {
                "actions": ["delete"], "before": {"name": guard.VALIDATION_RECORD + ".",
                    "zone_id": guard.ZONE, "type": "CNAME"}}}]
        self.assertEqual(len(guard.check_plan(p, SHA)), 1)
        p["resource_changes"][0]["change"]["before"]["zone_id"] = "OTHER"
        with self.assertRaises(SystemExit):
            guard.check_plan(p, SHA)


class CleanupTests(unittest.TestCase):
    def test_only_exact_not_found_errors_count_as_absence(self):
        for code, accepted in [("RepositoryNotFoundException", True),
                               ("AccessDeniedException", False), ("ThrottlingException", False)]:
            response = subprocess.CompletedProcess([], 254, "", f"An error occurred ({code})")
            with patch.object(cleanup.subprocess, "run", return_value=response):
                if accepted:
                    self.assertIsNone(cleanup.aws("ecr", "describe-repositories",
                        absent_codes=("RepositoryNotFoundException",)))
                else:
                    with self.assertRaises(SystemExit):
                        cleanup.aws("ecr", "describe-repositories",
                            absent_codes=("RepositoryNotFoundException",))

    def test_task_definition_absence_requires_exact_message(self):
        item = {"type": "aws_ecs_task_definition", "change": {"before": {"arn": "task:5"}}}
        for message, accepted in [("Unable to describe task definition.", True),
                                   ("Not authorized to describe task definition.", False)]:
            response = subprocess.CompletedProcess([], 254, "",
                "An error occurred (ClientException) when calling the "
                "DescribeTaskDefinition operation: " + message)
            with patch.object(cleanup.subprocess, "run", return_value=response):
                if accepted:
                    self.assertTrue(cleanup.removed(item))
                else:
                    with self.assertRaises(SystemExit):
                        cleanup.removed(item)

    def test_ecs_active_rejected_inactive_accepted(self):
        item = {"type": "aws_ecs_cluster", "change": {"before": {"arn": "cluster"}}}
        for status, expected in [("ACTIVE", False), ("INACTIVE", True)]:
            with patch.object(cleanup, "aws", return_value={"clusters": [{"status": status}]}):
                self.assertEqual(cleanup.removed(item), expected)
        with patch.object(cleanup, "aws", return_value={"clusters": [], "failures": [{"reason": "DENIED"}]}):
            with self.assertRaises(SystemExit):
                cleanup.removed(item)

    def test_nat_deleted_tombstone_and_active(self):
        item = {"type": "aws_nat_gateway", "change": {"before": {"id": "nat-id"}}}
        for state, expected in [("available", False), ("deleting", False), ("deleted", True)]:
            with patch.object(cleanup, "aws", return_value={"NatGateways": [{"State": state}]}) as aws_call:
                self.assertEqual(cleanup.removed(item), expected)
                aws_call.assert_called_once_with(
                    "ec2", "describe-nat-gateways", "--filter",
                    "Name=nat-gateway-id,Values=nat-id")

    def test_eip_keeps_plural_filters(self):
        item = {"type": "aws_eip", "change": {"before": {"id": "eipalloc-id"}}}
        with patch.object(cleanup, "aws", return_value={"Addresses": []}) as aws_call:
            self.assertTrue(cleanup.removed(item))
            aws_call.assert_called_once_with(
                "ec2", "describe-addresses", "--filters",
                "Name=allocation-id,Values=eipalloc-id")

    def test_recovery_dns_baseline_comes_from_original_log(self):
        records = [
            {"Name": "feras-dev.co.uk.", "Type": "NS"},
            {"Name": guard.APP_RECORD + ".", "Type": "A"},
            {"Name": guard.VALIDATION_RECORD + ".", "Type": "CNAME"},
        ]
        def write_log(archive):
            with ZipFile(archive, "w") as output:
                log = "\n".join(
                    "2026-09-26T12:00:00Z " + line
                    for line in json.dumps({"ResourceRecordSets": records}, indent=2).splitlines()
                )
                output.writestr(recovery.DNS_LOG, log)
        archive = io.BytesIO()
        write_log(archive)
        self.assertEqual(recovery.original_dns_records(archive), records)
        records.pop()
        archive = io.BytesIO()
        write_log(archive)
        with self.assertRaisesRegex(SystemExit, "lacks application records"):
            recovery.original_dns_records(archive)

    def test_recovery_preapply_metadata_requires_original_log(self):
        capture = {"state_before": {"VersionId": recovery.ORIGINAL_STATE_VERSION,
                                    "ServerSideEncryption": "AES256"},
                   "ecr_images_before_apply": recovery.ORIGINAL_ECR_IMAGES}
        archive = io.BytesIO()
        with ZipFile(archive, "w") as output:
            output.writestr(recovery.PREAPPLY_LOG,
                            "2026-09-26T12:00:00Z " + json.dumps(capture))
        self.assertEqual(recovery.original_preapply_baseline(archive), capture)
        capture["ecr_images_before_apply"] = 0
        archive = io.BytesIO()
        with ZipFile(archive, "w") as output:
            output.writestr(recovery.PREAPPLY_LOG,
                            "2026-09-26T12:00:00Z " + json.dumps(capture))
        with self.assertRaisesRegex(SystemExit, "ECR image count mismatch"):
            recovery.original_preapply_baseline(archive)

    def test_state_metadata_fail_closed(self):
        for response in [{"VersionId": "null", "ServerSideEncryption": "AES256"},
                         {"VersionId": "v1"}]:
            with patch.object(cleanup, "aws", return_value=response):
                with self.assertRaises(SystemExit):
                    cleanup.state_metadata()

    def test_success_and_remaining_state_or_unchanged_version(self):
        p = plan_fixture()
        baseline = {"protected_dns": [], "state": {"VersionId": "old"}, "ecr_image_count": 2}
        zone = {"HostedZone": {"Name": "feras-dev.co.uk.", "Config": {"PrivateZone": False}}}
        for state, version, error in [
            ({"resources": []}, "new", None),
            ({"resources": [{"mode": "managed", "instances": [{}]}]}, "new", "Managed resources"),
            ({"resources": []}, "old", "version did not change"),
        ]:
            with patch.dict(cleanup.os.environ, TF_VAR_image_tag=SHA), \
                 patch.object(cleanup, "removed", return_value=True), \
                 patch.object(cleanup.subprocess, "check_output", return_value=json.dumps(state)), \
                 patch.object(cleanup, "dns_records", return_value=[]), \
                 patch.object(cleanup, "aws", return_value=zone), \
                 patch.object(cleanup, "state_metadata", return_value={"VersionId": version}), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                if error:
                    with self.assertRaisesRegex(SystemExit, error):
                        cleanup.verify(p, baseline)
                else:
                    cleanup.verify(p, baseline)
                    self.assertIn('"result": "PASS"', output.getvalue())

    def test_retry_limit_and_retained_dns(self):
        p = plan_fixture()
        baseline = {"protected_dns": [], "state": {"VersionId": "old"}, "ecr_image_count": 2}
        with patch.dict(cleanup.os.environ, TF_VAR_image_tag=SHA), \
             patch.object(cleanup, "removed", return_value=False) as probe, \
             patch.object(cleanup.time, "sleep") as sleep, \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(SystemExit, "resources remain"):
                cleanup.verify(p, baseline)
            self.assertEqual(probe.call_count, 12)
            self.assertEqual(sleep.call_count, 11)
        for records, error in [([{"Name": guard.APP_RECORD + ".", "Type": "A"}], "Application DNS"),
                               ([{"Name": "other.", "Type": "TXT"}], "Retained DNS")]:
            with patch.dict(cleanup.os.environ, TF_VAR_image_tag=SHA), \
                 patch.object(cleanup, "removed", return_value=True), \
                 patch.object(cleanup.subprocess, "check_output", return_value='{"resources": []}'), \
                 patch.object(cleanup, "dns_records", return_value=records), \
                 contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(SystemExit, error):
                    cleanup.verify(p, baseline)


if __name__ == "__main__":
    unittest.main()
