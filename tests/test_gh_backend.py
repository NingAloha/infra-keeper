import importlib.util
import json
import pathlib
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "infra-keeper" / "scripts" / "gh_backend.py"
SPEC = importlib.util.spec_from_file_location("gh_backend", MODULE_PATH)
assert SPEC and SPEC.loader
GH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GH)


class GhBackendTests(unittest.TestCase):
    def test_parser_exposes_only_cli_commands(self):
        parser = GH.build_parser()
        commands = set(parser._subparsers._group_actions[0].choices)
        self.assertEqual(
            commands,
            {
                "authenticated-user",
                "repository",
                "list-commits",
                "get-file",
                "list-directory",
                "create-or-update-file",
                "delete-file",
            },
        )

    def test_write_requires_approval_without_calling_gh(self):
        args = GH.build_parser().parse_args(
            [
                "create-or-update-file",
                "--owner",
                "example",
                "--repo",
                "docs",
                "--path",
                "README.md",
                "--content",
                "new\n",
                "--commit-message",
                "docs: update README",
            ]
        )
        with patch.object(GH, "gh_api") as api:
            with self.assertRaises(GH.BackendError):
                GH.write_file(args)
        api.assert_not_called()

    def test_stale_sha_is_rejected_before_put(self):
        args = GH.build_parser().parse_args(
            [
                "create-or-update-file",
                "--owner",
                "example",
                "--repo",
                "docs",
                "--path",
                "README.md",
                "--content",
                "new\n",
                "--commit-message",
                "docs: update README",
                "--approved",
                "--expected-sha",
                "a" * 40,
            ]
        )
        with patch.object(
            GH,
            "gh_api",
            return_value={
                "type": "file",
                "path": "README.md",
                "sha": "b" * 40,
                "content": "b2xkCg==",
            },
        ) as api:
            with self.assertRaisesRegex(GH.BackendError, "changed since approval"):
                GH.write_file(args)
        api.assert_called_once()

    def test_json_output_shape_is_serializable(self):
        value = {"action": "create", "commit_sha": "abc"}
        self.assertEqual(json.loads(json.dumps(value)), value)


if __name__ == "__main__":
    unittest.main()
