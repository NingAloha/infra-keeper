import importlib.util
import json
import pathlib
import tempfile
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
                "read-state",
                "write-binding",
                "repository",
                "create-repository",
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
            side_effect=[
                {"login": "example"},
                {
                    "type": "file",
                    "path": "README.md",
                    "sha": "b" * 40,
                    "content": "b2xkCg==",
                },
            ],
        ) as api:
            with self.assertRaisesRegex(GH.BackendError, "changed since approval"):
                GH.write_file(args)
        self.assertEqual(
            [call.args for call in api.call_args_list],
            [("user",), ("repos/example/docs/contents/README.md",)],
        )

    def test_personal_owner_check_accepts_authenticated_user_case_insensitively(self):
        with patch.object(GH, "gh_api", return_value={"login": "Alice"}) as api:
            GH.enforce_personal_repository("alice", "docs")
        api.assert_called_once_with("user")

    def test_personal_owner_check_rejects_other_owner_before_repository_request(self):
        args = GH.build_parser().parse_args(
            ["repository", "--owner", "company", "--repo", "infrastructure"]
        )
        with patch.object(GH, "gh_api", return_value={"login": "alice"}) as api:
            with self.assertRaisesRegex(GH.BackendError, "organization, collaborator"):
                GH.repository_info(args)
        api.assert_called_once_with("user")

    def test_create_repository_requires_approval_without_calling_gh(self):
        args = GH.build_parser().parse_args(
            ["create-repository", "--owner", "alice", "--repo", "infrastructure"]
        )
        with patch.object(GH, "gh_api") as api, patch.object(GH, "run_gh_command") as command:
            with self.assertRaises(GH.BackendError):
                GH.create_repository(args)
        api.assert_not_called()
        command.assert_not_called()

    def test_create_repository_rejects_existing_name(self):
        args = GH.build_parser().parse_args(
            [
                "create-repository",
                "--owner",
                "alice",
                "--repo",
                "infrastructure",
                "--approved",
            ]
        )
        with patch.object(
            GH,
            "gh_api",
            side_effect=[{"login": "alice"}, {"full_name": "alice/infrastructure"}],
        ) as api, patch.object(GH, "run_gh_command") as command:
            with self.assertRaisesRegex(GH.BackendError, "already exists"):
                GH.create_repository(args)
        command.assert_not_called()
        self.assertEqual(
            [call.args for call in api.call_args_list],
            [("user",), ("repos/alice/infrastructure",)],
        )

    def test_create_repository_uses_private_readme_bootstrap(self):
        args = GH.build_parser().parse_args(
            [
                "create-repository",
                "--owner",
                "alice",
                "--repo",
                "infrastructure",
                "--approved",
            ]
        )
        with patch.object(
            GH,
            "gh_api",
            side_effect=[
                {"login": "alice"},
                GH.BackendError("GitHub CLI request failed: HTTP 404"),
                {
                    "full_name": "alice/infrastructure",
                    "visibility": "private",
                    "default_branch": "main",
                },
                [{"sha": "c" * 40}],
            ],
        ) as api, patch.object(GH, "run_gh_command") as command:
            result = GH.create_repository(args)
        self.assertEqual(result["repository"], "alice/infrastructure")
        self.assertEqual(result["initial_commit_sha"], "c" * 40)
        command.assert_called_once_with(
            [
                "gh",
                "repo",
                "create",
                "alice/infrastructure",
                "--private",
                "--add-readme",
                "--description",
                "InfraKeeper infrastructure documentation",
            ]
        )
        self.assertEqual(len(api.call_args_list), 4)

    def test_json_output_shape_is_serializable(self):
        value = {"action": "create", "commit_sha": "abc"}
        self.assertEqual(json.loads(json.dumps(value)), value)

    def test_state_requires_verification_marker(self):
        args = GH.build_parser().parse_args(
            [
                "write-binding",
                "--owner",
                "alice",
                "--repo",
                "infrastructure",
                "--bootstrap-status",
                "created",
                "--initial-commit-sha",
                "c" * 40,
            ]
        )
        with patch.object(GH, "save_state") as save:
            with self.assertRaisesRegex(GH.BackendError, "--verified"):
                GH.write_binding(args)
        save.assert_not_called()

    def test_state_round_trip_contains_no_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "state.json"
            with patch.object(GH, "state_path", return_value=path):
                args = GH.build_parser().parse_args(
                    [
                        "write-binding",
                        "--owner",
                        "Alice",
                        "--repo",
                        "infrastructure",
                        "--bootstrap-status",
                        "created",
                        "--initial-commit-sha",
                        "c" * 40,
                        "--verified",
                    ]
                )
                result = GH.write_binding(args)
                loaded = GH.read_state(args)
            self.assertEqual(result["repository"], "Alice/infrastructure")
            self.assertTrue(loaded["present"])
            self.assertEqual(loaded["binding"]["branch"], "main")
            self.assertEqual(loaded["bootstrap"]["initial_commit_sha"], "c" * 40)
            self.assertNotIn("token", path.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
