#!/usr/bin/env python3
"""Safe JSON CLI wrapper around GitHub's Contents API via ``gh api``.

This is a Skill support script, not an MCP server. It keeps GitHub
authentication in the user's existing gh credential store and never accepts
or writes tokens. Commands print JSON to stdout and diagnostics to stderr.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


GH_TIMEOUT_SECONDS = 30
OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,38})$")
REPO_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,99})$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
STATE_VERSION = 1


class BackendError(Exception):
    """An expected error that can be shown without a traceback."""


def redact(text: str) -> str:
    text = re.sub(r"(?i)bearer\s+[^\s,;]+", "Bearer [REDACTED]", text)
    return re.sub(r"(?:ghp|github_pat)_[A-Za-z0-9_]+", "[REDACTED]", text)


def required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BackendError(f"{name} must be a non-empty string")
    return value.strip()


def state_path() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "InfraKeeper"
    elif os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "InfraKeeper"
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "infra-keeper"
    return base / "state.json"


def split_repository(value: Any) -> tuple[str, str]:
    value = required_text(value, "repository")
    parts = value.split("/")
    if len(parts) != 2:
        raise BackendError("repository must be in OWNER/REPO form")
    return repository(parts[0], parts[1])


def load_state() -> dict[str, Any] | None:
    path = state_path()
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise BackendError(f"could not read local InfraKeeper state: {redact(str(exc))}") from exc
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BackendError("local InfraKeeper state is not valid JSON") from exc
    if not isinstance(value, dict) or value.get("version") != STATE_VERSION:
        raise BackendError("local InfraKeeper state has an unsupported version")
    binding = value.get("binding")
    if not isinstance(binding, dict):
        raise BackendError("local InfraKeeper state has no binding")
    owner, repo = split_repository(binding.get("repository"))
    if binding.get("branch") != "main":
        raise BackendError("local InfraKeeper state is not bound to main")
    bootstrap = value.get("bootstrap")
    if not isinstance(bootstrap, dict) or bootstrap.get("status") not in {"created", "reused"}:
        raise BackendError("local InfraKeeper state has no valid bootstrap status")
    normalized: dict[str, Any] = {
        "version": STATE_VERSION,
        "binding": {"repository": f"{owner}/{repo}", "branch": "main"},
        "bootstrap": {"status": bootstrap["status"]},
    }
    if "initial_commit_sha" in bootstrap:
        normalized["bootstrap"]["initial_commit_sha"] = sha(
            bootstrap["initial_commit_sha"], "initial-commit-sha"
        )
    return normalized


def save_state(value: dict[str, Any]) -> None:
    path = state_path()
    temporary: Path | None = None
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            path.parent.chmod(0o700)
        except OSError:
            pass
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix="state.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
        try:
            path.chmod(0o600)
        except OSError:
            pass
    except OSError as exc:
        raise BackendError(f"could not write local InfraKeeper state: {redact(str(exc))}") from exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def repository(owner: str, repo: str) -> tuple[str, str]:
    owner = required_text(owner, "owner")
    repo = required_text(repo, "repo")
    if not OWNER_RE.fullmatch(owner):
        raise BackendError("owner contains unsupported characters")
    if not REPO_RE.fullmatch(repo):
        raise BackendError("repo contains unsupported characters")
    return owner, repo


def branch(value: str) -> str:
    value = required_text(value, "branch")
    if len(value) > 255 or "\x00" in value or value.startswith("-"):
        raise BackendError("branch contains unsupported characters")
    if ".." in value or value.endswith("/") or value.endswith("."):
        raise BackendError("branch is not a valid Git ref")
    return value


def repo_path(value: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise BackendError("path must be a string")
    if allow_empty and value == "":
        return value
    if not value or value.startswith("/") or "\x00" in value:
        raise BackendError("path must be a relative repository path")
    if any(part in {"", ".", ".."} for part in value.split("/")):
        raise BackendError("path must not contain empty, '.' or '..' segments")
    return value


def sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise BackendError(f"{name} must be a hexadecimal blob or commit SHA")
    return value


def endpoint(owner: str, repo: str, suffix: str = "") -> str:
    suffix = suffix.strip("/")
    return f"repos/{owner}/{repo}/{suffix}" if suffix else f"repos/{owner}/{repo}"


def gh_api(
    path: str,
    *,
    method: str = "GET",
    query: dict[str, str] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    command = ["gh", "api", path, "--method", method]
    for key, value in (query or {}).items():
        command.extend(["--raw-field", f"{key}={value}"])
    input_text = None
    if body is not None:
        command.extend(["--input", "-"])
        input_text = json.dumps(body, ensure_ascii=False)
    try:
        result = subprocess.run(
            command,
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
            timeout=GH_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise BackendError("GitHub CLI 'gh' is not installed or is not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise BackendError("GitHub CLI request timed out after 30 seconds") from exc
    except OSError as exc:
        raise BackendError(f"could not start GitHub CLI: {redact(str(exc))}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown gh error"
        raise BackendError(f"GitHub CLI request failed: {redact(detail)}")
    if not result.stdout.strip():
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise BackendError("GitHub CLI returned a non-JSON response") from exc


def run_gh_command(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=GH_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise BackendError("GitHub CLI 'gh' is not installed or is not on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise BackendError("GitHub CLI request timed out after 30 seconds") from exc
    except OSError as exc:
        raise BackendError(f"could not start GitHub CLI: {redact(str(exc))}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown gh error"
        raise BackendError(f"GitHub CLI request failed: {redact(detail)}")
    return result.stdout.strip()


def current_file(owner: str, repo: str, path: str, ref: str) -> dict[str, Any]:
    result = gh_api(endpoint(owner, repo, f"contents/{path}"), query={"ref": ref})
    if not isinstance(result, dict) or result.get("type") != "file":
        raise BackendError("the requested path is not a regular file")
    encoded = result.get("content", "")
    try:
        raw = base64.b64decode(encoded, validate=False)
    except (TypeError, ValueError) as exc:
        raise BackendError("GitHub returned invalid base64 file content") from exc
    try:
        text = raw.decode("utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        text = None
        encoding = "base64"
    return {
        "path": result.get("path", path),
        "sha": result.get("sha"),
        "size": result.get("size", len(raw)),
        "html_url": result.get("html_url"),
        "encoding": encoding,
        "content": text,
        "content_base64": base64.b64encode(raw).decode("ascii"),
    }


def head_sha(owner: str, repo: str, ref: str) -> str:
    result = gh_api(endpoint(owner, repo, f"git/ref/heads/{ref}"))
    try:
        return result["object"]["sha"]
    except (KeyError, TypeError) as exc:
        raise BackendError("GitHub returned an unexpected branch reference") from exc


def check_head(owner: str, repo: str, ref: str, expected: str | None) -> None:
    if expected is None:
        return
    expected = sha(expected, "expected-head-sha")
    actual = head_sha(owner, repo, ref)
    if actual != expected:
        raise BackendError(
            f"branch HEAD changed since approval (expected {expected}, current {actual})"
        )


def read_file(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    return current_file(owner, repo, repo_path(args.path), branch(args.branch))


def list_directory(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    ref = branch(args.branch)
    path = repo_path(args.path, allow_empty=True)
    result = gh_api(
        endpoint(owner, repo, f"contents/{path}" if path else "contents"),
        query={"ref": ref},
    )
    if not isinstance(result, list):
        raise BackendError("the requested path is not a directory")
    return {"path": path, "branch": ref, "entries": result}


def list_commits(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    ref = branch(args.branch)
    if not 1 <= args.per_page <= 100:
        raise BackendError("per-page must be from 1 to 100")
    result = gh_api(
        endpoint(owner, repo, "commits"),
        query={"sha": ref, "per_page": str(args.per_page)},
    )
    if not isinstance(result, list):
        raise BackendError("GitHub returned an unexpected commits response")
    return {"branch": ref, "commits": result}


def repository_info(args: argparse.Namespace) -> Any:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    return gh_api(endpoint(owner, repo))


def authenticated_user(_: argparse.Namespace) -> Any:
    return gh_api("user")


def read_state(_: argparse.Namespace) -> dict[str, Any]:
    value = load_state()
    if value is None:
        return {"action": "read-state", "present": False}
    return {"action": "read-state", "present": True, **value}


def write_binding(args: argparse.Namespace) -> dict[str, Any]:
    if not args.verified:
        raise BackendError("--verified is required after successful repository verification")
    owner, repo = repository(args.owner, args.repo)
    ref = branch(args.branch)
    if ref != "main":
        raise BackendError("InfraKeeper bindings must use the main branch")
    bootstrap: dict[str, Any] = {"status": args.bootstrap_status}
    if args.bootstrap_status == "created":
        bootstrap["initial_commit_sha"] = sha(args.initial_commit_sha, "initial-commit-sha")
    elif args.initial_commit_sha is not None:
        bootstrap["initial_commit_sha"] = sha(args.initial_commit_sha, "initial-commit-sha")
    value = {
        "version": STATE_VERSION,
        "binding": {"repository": f"{owner}/{repo}", "branch": ref},
        "bootstrap": bootstrap,
    }
    save_state(value)
    return {
        "action": "write-state",
        "repository": f"{owner}/{repo}",
        "branch": ref,
        "bootstrap": bootstrap,
    }


def authenticated_login() -> str:
    result = gh_api("user")
    if not isinstance(result, dict):
        raise BackendError("GitHub returned an unexpected authenticated-user response")
    try:
        return required_text(result["login"], "authenticated user login")
    except (KeyError, TypeError) as exc:
        raise BackendError("GitHub returned no authenticated user login") from exc


def enforce_personal_repository(owner: str, repo: str) -> None:
    current_login = authenticated_login()
    if owner.casefold() != current_login.casefold():
        raise BackendError(
            "target repository owner must match the authenticated GitHub user; "
            "organization, collaborator and other-user repositories are not allowed"
        )


def create_repository(args: argparse.Namespace) -> dict[str, Any]:
    if not args.approved:
        raise BackendError("--approved is required after explicit bounded user approval")
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)

    try:
        gh_api(endpoint(owner, repo))
    except BackendError as exc:
        if "404" not in str(exc):
            raise
    else:
        raise BackendError("repository already exists; choose a different repository name")

    description = required_text(args.description, "description")
    visibility_flag = "--private" if args.visibility == "private" else "--public"
    run_gh_command(
        [
            "gh",
            "repo",
            "create",
            f"{owner}/{repo}",
            visibility_flag,
            "--add-readme",
            "--description",
            description,
        ]
    )
    info = gh_api(endpoint(owner, repo))
    if not isinstance(info, dict):
        raise BackendError("repository was created but GitHub returned no repository metadata")
    default_branch = info.get("default_branch")
    if default_branch != "main":
        raise BackendError(
            f"repository was created, but its default branch is {default_branch!r}, not 'main'"
        )
    commits = gh_api(
        endpoint(owner, repo, "commits"),
        query={"sha": "main", "per_page": "1"},
    )
    if not isinstance(commits, list) or not commits or not isinstance(commits[0], dict):
        raise BackendError("repository was created but its initial commit could not be verified")
    initial_commit_sha = commits[0].get("sha")
    if not isinstance(initial_commit_sha, str) or not initial_commit_sha:
        raise BackendError("repository was created but GitHub returned no initial commit SHA")
    return {
        "action": "create-repository",
        "repository": info.get("full_name", f"{owner}/{repo}"),
        "visibility": info.get("visibility", args.visibility),
        "default_branch": default_branch,
        "initial_commit_sha": initial_commit_sha,
    }


def write_file(args: argparse.Namespace) -> dict[str, Any]:
    if not args.approved:
        raise BackendError("--approved is required after explicit bounded user approval")
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    path = repo_path(args.path)
    ref = branch(args.branch)
    message = required_text(args.commit_message, "commit-message")
    check_head(owner, repo, ref, args.expected_head_sha)

    if args.content_file:
        try:
            content = Path(args.content_file).read_text(encoding="utf-8")
        except OSError as exc:
            raise BackendError(f"could not read content file: {redact(str(exc))}") from exc
    else:
        content = args.content
    if not isinstance(content, str):
        raise BackendError("one of --content or --content-file is required")

    existing: dict[str, Any] | None = None
    try:
        existing = current_file(owner, repo, path, ref)
    except BackendError as exc:
        if "GitHub CLI request failed" not in str(exc) or "404" not in str(exc):
            raise

    expected = args.expected_sha
    if existing is not None:
        if expected is None:
            raise BackendError(
                f"file already exists with SHA {existing.get('sha')}; --expected-sha is required"
            )
        expected = sha(expected, "expected-sha")
        if expected != existing.get("sha"):
            raise BackendError(
                f"file changed since approval (expected {expected}, current {existing.get('sha')})"
            )
    elif expected is not None:
        raise BackendError("--expected-sha must be omitted when creating a new file")

    body: dict[str, Any] = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": ref,
    }
    if expected is not None:
        body["sha"] = expected
    result = gh_api(endpoint(owner, repo, f"contents/{path}"), method="PUT", body=body)
    return {
        "action": "update" if existing is not None else "create",
        "path": path,
        "branch": ref,
        "content_sha": (result or {}).get("content", {}).get("sha"),
        "commit_sha": (result or {}).get("commit", {}).get("sha"),
    }


def delete_file(args: argparse.Namespace) -> dict[str, Any]:
    if not args.approved:
        raise BackendError("--approved is required after explicit bounded user approval")
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    path = repo_path(args.path)
    ref = branch(args.branch)
    expected = sha(args.expected_sha, "expected-sha")
    check_head(owner, repo, ref, args.expected_head_sha)
    existing = current_file(owner, repo, path, ref)
    if expected != existing.get("sha"):
        raise BackendError(
            f"file changed since approval (expected {expected}, current {existing.get('sha')})"
        )
    result = gh_api(
        endpoint(owner, repo, f"contents/{path}"),
        method="DELETE",
        body={"message": required_text(args.commit_message, "commit-message"), "sha": expected, "branch": ref},
    )
    return {"action": "delete", "path": path, "branch": ref, "commit_sha": (result or {}).get("commit", {}).get("sha")}


def add_repository_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)


def add_ref_args(parser: argparse.ArgumentParser) -> None:
    add_repository_args(parser)
    parser.add_argument("--branch", default="main")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    user_parser = subparsers.add_parser("authenticated-user")
    user_parser.set_defaults(handler=authenticated_user)

    state_read_parser = subparsers.add_parser("read-state")
    state_read_parser.set_defaults(handler=read_state)

    state_write_parser = subparsers.add_parser("write-binding")
    add_repository_args(state_write_parser)
    state_write_parser.add_argument("--branch", default="main")
    state_write_parser.add_argument("--bootstrap-status", choices=("created", "reused"), required=True)
    state_write_parser.add_argument("--initial-commit-sha")
    state_write_parser.add_argument("--verified", action="store_true")
    state_write_parser.set_defaults(handler=write_binding)

    info_parser = subparsers.add_parser("repository")
    add_repository_args(info_parser)
    info_parser.set_defaults(handler=repository_info)

    create_repo_parser = subparsers.add_parser("create-repository")
    add_repository_args(create_repo_parser)
    create_repo_parser.add_argument("--visibility", choices=("private", "public"), default="private")
    create_repo_parser.add_argument(
        "--description",
        default="InfraKeeper infrastructure documentation",
    )
    create_repo_parser.add_argument("--approved", action="store_true")
    create_repo_parser.set_defaults(handler=create_repository)

    commits_parser = subparsers.add_parser("list-commits")
    add_ref_args(commits_parser)
    commits_parser.add_argument("--per-page", type=int, default=10)
    commits_parser.set_defaults(handler=list_commits)

    file_parser = subparsers.add_parser("get-file")
    add_ref_args(file_parser)
    file_parser.add_argument("--path", required=True)
    file_parser.set_defaults(handler=read_file)

    directory_parser = subparsers.add_parser("list-directory")
    add_ref_args(directory_parser)
    directory_parser.add_argument("--path", default="")
    directory_parser.set_defaults(handler=list_directory)

    write_parser = subparsers.add_parser("create-or-update-file")
    add_ref_args(write_parser)
    write_parser.add_argument("--path", required=True)
    content = write_parser.add_mutually_exclusive_group(required=True)
    content.add_argument("--content")
    content.add_argument("--content-file")
    write_parser.add_argument("--commit-message", required=True)
    write_parser.add_argument("--approved", action="store_true")
    write_parser.add_argument("--expected-sha")
    write_parser.add_argument("--expected-head-sha")
    write_parser.set_defaults(handler=write_file)

    delete_parser = subparsers.add_parser("delete-file")
    add_ref_args(delete_parser)
    delete_parser.add_argument("--path", required=True)
    delete_parser.add_argument("--commit-message", required=True)
    delete_parser.add_argument("--approved", action="store_true")
    delete_parser.add_argument("--expected-sha", required=True)
    delete_parser.add_argument("--expected-head-sha")
    delete_parser.set_defaults(handler=delete_file)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        value = args.handler(args)
    except BackendError as exc:
        print(f"error: {redact(str(exc))}", file=sys.stderr)
        return 2
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
