#!/usr/bin/env python3
"""Safe JSON CLI wrapper around GitHub's Contents API via ``gh api``.

This is a Skill support script. It keeps GitHub authentication in the user's
existing gh credential store and never accepts or writes tokens. Commands print
JSON to stdout and diagnostics to stderr.
"""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

if os.name == "nt":
    import msvcrt
else:
    import fcntl


GH_TIMEOUT_SECONDS = 30
OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,38})$")
REPO_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,99})$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,64}$")
DEVICE_ID_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]{0,31})$")
STATE_VERSION = 5
SUPPORTED_STATE_VERSIONS = {1, 2, 3, 4, STATE_VERSION}


class BackendError(Exception):
    """An expected error that can be shown without a traceback."""


def redact(text: str) -> str:
    text = re.sub(r"(?i)bearer\s+[^\s,;]+", "Bearer [REDACTED]", text)
    return re.sub(r"(?:ghp|github_pat)_[A-Za-z0-9_]+", "[REDACTED]", text)


def required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BackendError(f"{name} must be a non-empty string")
    return value.strip()


def device_id(value: Any) -> str:
    value = required_text(value, "device-id")
    if not DEVICE_ID_RE.fullmatch(value):
        raise BackendError("device-id must use 1-32 letters, digits, '.', '_' or '-' characters")
    return value


def device_branch(device: str) -> str:
    return f"infra/device/{device}"


def state_path() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "InfraKeeper"
    elif os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "InfraKeeper"
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")) / "infra-keeper"
    return base / "state.json"


def state_lock_path() -> Path:
    return state_path().with_name("state.json.lock")


@contextmanager
def state_lock():
    """Serialize local state replacement across concurrent helper processes."""
    path = state_path()
    lock_path = state_lock_path()
    try:
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            path.parent.chmod(0o700)
        except OSError:
            pass
        with lock_path.open("a+") as handle:
            try:
                lock_path.chmod(0o600)
            except OSError:
                pass
            if os.name == "nt":
                handle.seek(0)
                handle.write("0")
                handle.flush()
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if os.name == "nt":
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError as exc:
        raise BackendError(f"could not lock local InfraKeeper state: {redact(str(exc))}") from exc


def disk_state_revision(path: Path) -> int | None:
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
    if not isinstance(value, dict):
        raise BackendError("local InfraKeeper state is not a JSON object")
    revision = value.get("revision", 0)
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise BackendError("local InfraKeeper state has an invalid revision")
    return revision


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
    if not isinstance(value, dict) or value.get("version") not in SUPPORTED_STATE_VERSIONS:
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
    branches: dict[str, str] = {}
    revision = value.get("revision", 0)
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise BackendError("local InfraKeeper state has an invalid revision")
    if isinstance(binding.get("branches"), dict):
        for branch_name, branch_head in binding["branches"].items():
            branches[branch(branch_name)] = sha(branch_head, f"{branch_name}-head-sha")
    elif "head_sha" in binding:
        branches["main"] = sha(binding["head_sha"], "head-sha")
    normalized: dict[str, Any] = {
        "version": STATE_VERSION,
        "revision": revision,
        "binding": {"repository": f"{owner}/{repo}", "branch": "main", "branches": branches},
        "bootstrap": {"status": bootstrap["status"]},
    }
    if "device_id" in binding:
        current_device_id = device_id(binding["device_id"])
        expected_device_branch = device_branch(current_device_id)
        stored_device_branch = binding.get("device_branch", expected_device_branch)
        if stored_device_branch != expected_device_branch:
            raise BackendError("local InfraKeeper state has an invalid device branch")
        normalized["binding"]["device_id"] = current_device_id
        normalized["binding"]["device_branch"] = expected_device_branch
        if "device_head_sha" in binding:
            device_head = sha(binding["device_head_sha"], "device-head-sha")
            normalized["binding"]["branches"][expected_device_branch] = device_head
    if "initial_commit_sha" in bootstrap:
        normalized["bootstrap"]["initial_commit_sha"] = sha(
            bootstrap["initial_commit_sha"], "initial-commit-sha"
        )
    return normalized


def save_state(value: dict[str, Any], *, expected_revision: int | None) -> None:
    path = state_path()
    temporary: Path | None = None
    try:
        with state_lock():
            current_revision = disk_state_revision(path)
            if current_revision != expected_revision:
                raise BackendError(
                    "local InfraKeeper state changed concurrently; re-read state before continuing"
                )
            value = dict(value)
            value["version"] = STATE_VERSION
            value["revision"] = 0 if current_revision is None else current_revision + 1
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


def require_bound_repository(owner: str, repo: str) -> dict[str, Any]:
    state = load_state()
    if state is None:
        raise BackendError(
            "local InfraKeeper binding state is absent; use the setup or explicit rebind flow"
        )
    stored_owner, stored_repo = split_repository(state["binding"]["repository"])
    if (stored_owner.casefold(), stored_repo.casefold()) != (owner.casefold(), repo.casefold()):
        raise BackendError("local binding does not match the requested repository")
    return state


def require_read_scope(args: argparse.Namespace, owner: str, repo: str) -> None:
    state = load_state()
    if args.setup:
        if state is not None:
            raise BackendError("a local binding already exists; use the explicit rebind flow")
        return
    if args.rebind:
        if state is None:
            raise BackendError("the explicit rebind flow requires an existing local binding")
        return
    if state is None:
        raise BackendError(
            "local InfraKeeper binding state is absent; use the setup or explicit rebind flow"
        )
    stored_owner, stored_repo = split_repository(state["binding"]["repository"])
    if (stored_owner.casefold(), stored_repo.casefold()) != (owner.casefold(), repo.casefold()):
        raise BackendError("local binding does not match the requested repository")


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
        return sha(result["object"]["sha"], "remote-head-sha")
    except (KeyError, TypeError) as exc:
        raise BackendError("GitHub returned an unexpected branch reference") from exc


def compare_heads(owner: str, repo: str, base: str, head: str) -> dict[str, Any]:
    result = gh_api(endpoint(owner, repo, f"compare/{base}...{head}"))
    if not isinstance(result, dict):
        raise BackendError("GitHub returned an unexpected commit comparison response")
    status = result.get("status")
    if status not in {"ahead", "behind", "diverged", "identical"}:
        raise BackendError("GitHub returned an unknown commit comparison status")
    ahead_by = result.get("ahead_by")
    behind_by = result.get("behind_by")
    if not isinstance(ahead_by, int) or not isinstance(behind_by, int):
        raise BackendError("GitHub returned invalid commit comparison counts")
    return {"status": status, "ahead_by": ahead_by, "behind_by": behind_by}


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
    require_read_scope(args, owner, repo)
    return current_file(owner, repo, repo_path(args.path), branch(args.branch))


def list_directory(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    require_read_scope(args, owner, repo)
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
    require_read_scope(args, owner, repo)
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


def repository_head(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    require_read_scope(args, owner, repo)
    ref = branch(args.branch)
    return {
        "repository": f"{owner}/{repo}",
        "branch": ref,
        "head_sha": head_sha(owner, repo, ref),
    }


def branch_head(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    require_read_scope(args, owner, repo)
    ref = branch(args.branch)
    return {
        "repository": f"{owner}/{repo}",
        "branch": ref,
        "head_sha": head_sha(owner, repo, ref),
    }


def list_device_branches(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    require_read_scope(args, owner, repo)
    result = gh_api(endpoint(owner, repo, "git/matching-refs/heads/infra/device/"))
    if result is None:
        result = []
    if not isinstance(result, list):
        raise BackendError("GitHub returned an unexpected device-branch response")
    branches: list[dict[str, str]] = []
    for item in result:
        if not isinstance(item, dict):
            raise BackendError("GitHub returned an invalid device-branch entry")
        raw_ref = item.get("ref")
        if not isinstance(raw_ref, str) or not raw_ref.startswith("refs/heads/"):
            continue
        ref = raw_ref.removeprefix("refs/heads/")
        if not is_device_branch(ref):
            continue
        obj = item.get("object")
        if not isinstance(obj, dict):
            raise BackendError("GitHub returned no object for a device branch")
        branches.append(
            {
                "device_id": ref.removeprefix("infra/device/"),
                "branch": ref,
                "head_sha": sha(obj.get("sha"), "device-branch-head-sha"),
            }
        )
    branches.sort(key=lambda item: item["device_id"].casefold())
    return {"action": "list-device-branches", "repository": f"{owner}/{repo}", "branches": branches}


def repository_info(args: argparse.Namespace) -> Any:
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    require_read_scope(args, owner, repo)
    return gh_api(endpoint(owner, repo))


def authenticated_user(_: argparse.Namespace) -> Any:
    return gh_api("user")


def read_state(_: argparse.Namespace) -> dict[str, Any]:
    value = load_state()
    if value is None:
        return {"action": "read-state", "present": False}
    return {"action": "read-state", "present": True, **value}


def branch_checkpoint(state: dict[str, Any], ref: str) -> str | None:
    return state["binding"].get("branches", {}).get(ref)


def set_branch_checkpoint(state: dict[str, Any], ref: str, value: str) -> None:
    state.setdefault("binding", {}).setdefault("branches", {})[ref] = sha(value, f"{ref}-head-sha")


def is_device_branch(ref: str) -> bool:
    prefix, _, value = ref.partition("infra/device/")
    return prefix == "" and bool(value) and DEVICE_ID_RE.fullmatch(value) is not None


def require_bound_device_state(owner: str, repo: str) -> tuple[dict[str, Any], str]:
    state = require_bound_repository(owner, repo)
    bound_branch = state["binding"].get("device_branch")
    if not isinstance(bound_branch, str):
        raise BackendError("local binding has no device branch; configure this device first")
    return state, bound_branch


def bind_device(args: argparse.Namespace) -> dict[str, Any]:
    if not args.verified:
        raise BackendError("--verified is required after successful repository verification")
    owner, repo = repository(args.owner, args.repo)
    ref = branch(args.branch)
    if ref != "main":
        raise BackendError("InfraKeeper bindings must use the main branch")
    enforce_personal_repository(owner, repo)
    state = load_state()
    if state is None:
        raise BackendError("local InfraKeeper binding state is absent")
    stored_owner, stored_repo = split_repository(state["binding"]["repository"])
    if (stored_owner.casefold(), stored_repo.casefold()) != (owner.casefold(), repo.casefold()):
        raise BackendError("local binding does not match the requested repository")
    current_device_id = device_id(args.device_id)
    previous_device_id = state["binding"].get("device_id")
    if previous_device_id is not None:
        previous_device_id = device_id(previous_device_id)
        if previous_device_id != current_device_id:
            if not args.rebind_device:
                raise BackendError(
                    "changing the bound device requires the explicit --rebind-device flow"
                )
            if not args.approved:
                raise BackendError(
                    "--approved is required for the separate device rebind approval"
                )
        elif args.rebind_device:
            raise BackendError("--rebind-device is only valid when changing the device identity")
    elif args.rebind_device:
        raise BackendError("--rebind-device requires an existing bound device")
    state["version"] = STATE_VERSION
    state["binding"]["device_id"] = current_device_id
    state["binding"]["device_branch"] = device_branch(current_device_id)
    state["binding"].pop("device_head_sha", None)
    save_state(state, expected_revision=state["revision"])
    return {
        "action": "bind-device",
        "repository": f"{owner}/{repo}",
        "device_id": current_device_id,
        "device_branch": device_branch(current_device_id),
        "rebound": previous_device_id is not None and previous_device_id != current_device_id,
    }


def ensure_device_branch(args: argparse.Namespace) -> dict[str, Any]:
    if not args.approved:
        raise BackendError("--approved is required after explicit branch-creation approval")
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    state, ref = require_bound_device_state(owner, repo)
    current_main = head_sha(owner, repo, "main")
    expected_main = sha(args.main_head_sha, "main-head-sha")
    if current_main != expected_main:
        raise BackendError(
            f"main changed before device branch creation (expected {args.main_head_sha}, current {current_main})"
        )
    created = False
    try:
        current_branch = head_sha(owner, repo, ref)
    except BackendError as exc:
        if "404" not in str(exc):
            raise
        gh_api(
            endpoint(owner, repo, "git/refs"),
            method="POST",
            body={"ref": f"refs/heads/{ref}", "sha": current_main},
        )
        current_branch = head_sha(owner, repo, ref)
        created = True
    previous_branch = branch_checkpoint(state, ref)
    if previous_branch is not None and previous_branch != current_branch:
        comparison = compare_heads(owner, repo, previous_branch, current_branch)
        if comparison["status"] not in {"identical", "ahead"} or comparison["behind_by"] != 0:
            raise BackendError(
                f"device branch {ref} is not a normal descendant of the local checkpoint; "
                f"comparison={comparison['status']}"
            )
    state["version"] = STATE_VERSION
    set_branch_checkpoint(state, ref, current_branch)
    save_state(state, expected_revision=state["revision"])
    return {
        "action": "ensure-device-branch",
        "repository": f"{owner}/{repo}",
        "branch": ref,
        "head_sha": current_branch,
        "main_head_sha": current_main,
        "created": created,
        "previous_head_sha": previous_branch,
    }


def sync_binding_head(args: argparse.Namespace) -> dict[str, Any]:
    owner, repo = repository(args.owner, args.repo)
    ref = branch(args.branch)
    if ref != "main" and not is_device_branch(ref):
        raise BackendError("only main or an infra/device/<device-id> branch can be synchronized")
    enforce_personal_repository(owner, repo)
    state = load_state()
    if state is None:
        raise BackendError("local InfraKeeper binding state is absent")
    stored_owner, stored_repo = split_repository(state["binding"]["repository"])
    if (stored_owner.casefold(), stored_repo.casefold()) != (owner.casefold(), repo.casefold()):
        raise BackendError("local binding does not match the requested repository")
    stored_head = branch_checkpoint(state, ref)
    current_head = head_sha(owner, repo, ref)
    if stored_head is None:
        if args.activate:
            state["version"] = STATE_VERSION
            set_branch_checkpoint(state, ref, current_head)
            save_state(state, expected_revision=state["revision"])
            return {
                "action": "sync-binding-head",
                "status": "ready",
                "repository": f"{owner}/{repo}",
                "branch": ref,
                "previous_head_sha": None,
                "head_sha": current_head,
                "comparison": None,
                "state_updated": True,
                "activated": True,
            }
        return {
            "action": "sync-binding-head",
            "status": "missing-checkpoint",
            "repository": f"{owner}/{repo}",
            "branch": ref,
            "head_sha": current_head,
            "state_updated": False,
        }
    comparison = compare_heads(owner, repo, stored_head, current_head)
    if comparison["status"] in {"identical", "ahead"} and comparison["behind_by"] == 0:
        state["version"] = STATE_VERSION
        set_branch_checkpoint(state, ref, current_head)
        state_updated = current_head != stored_head
        if state_updated:
            save_state(state, expected_revision=state["revision"])
        return {
            "action": "sync-binding-head",
            "status": "ready",
            "repository": f"{owner}/{repo}",
            "branch": ref,
            "previous_head_sha": stored_head,
            "head_sha": current_head,
            "comparison": comparison,
            "state_updated": state_updated,
        }
    return {
        "action": "sync-binding-head",
        "status": "changed-since-state",
        "repository": f"{owner}/{repo}",
        "branch": ref,
        "previous_head_sha": stored_head,
        "head_sha": current_head,
        "comparison": comparison,
        "state_updated": False,
    }


def record_bound_head(owner: str, repo: str, ref: str, new_head: str) -> dict[str, Any]:
    """Best-effort local state update after a successful GitHub write."""
    try:
        state = load_state()
    except BackendError as exc:
        return {"state_updated": False, "state_update_reason": redact(str(exc))}
    if state is None:
        return {"state_updated": False, "state_update_reason": "local binding state is absent"}
    stored_owner, stored_repo = split_repository(state["binding"]["repository"])
    if (stored_owner.casefold(), stored_repo.casefold()) != (owner.casefold(), repo.casefold()):
        return {"state_updated": False, "state_update_reason": "local binding does not match repository"}
    state["version"] = STATE_VERSION
    if ref != "main" and state["binding"].get("device_branch") != ref:
        return {"state_updated": False, "state_update_reason": "binding branch does not match repository"}
    set_branch_checkpoint(state, ref, new_head)
    try:
        save_state(state, expected_revision=state["revision"])
    except BackendError as exc:
        return {"state_updated": False, "state_update_reason": redact(str(exc))}
    return {"state_updated": True}


def write_binding(args: argparse.Namespace) -> dict[str, Any]:
    if not args.verified:
        raise BackendError("--verified is required after successful repository verification")
    if not (args.setup or args.rebind):
        raise BackendError("--setup or --rebind is required for binding changes")
    owner, repo = repository(args.owner, args.repo)
    ref = branch(args.branch)
    if ref != "main":
        raise BackendError("InfraKeeper bindings must use the main branch")
    enforce_personal_repository(owner, repo)
    existing_state = load_state()
    if args.setup and existing_state is not None:
        raise BackendError("a local binding already exists; use the explicit rebind flow")
    if args.rebind and existing_state is None:
        raise BackendError("the explicit rebind flow requires an existing local binding")
    head = sha(args.head_sha, "head-sha")
    current_device_id = device_id(args.device_id)
    bootstrap: dict[str, Any] = {"status": args.bootstrap_status}
    if args.bootstrap_status == "created":
        bootstrap["initial_commit_sha"] = sha(args.initial_commit_sha, "initial-commit-sha")
    elif args.initial_commit_sha is not None:
        bootstrap["initial_commit_sha"] = sha(args.initial_commit_sha, "initial-commit-sha")
    value = {
        "version": STATE_VERSION,
        "binding": {
            "repository": f"{owner}/{repo}",
            "branch": ref,
            "branches": {"main": head},
            "device_id": current_device_id,
            "device_branch": device_branch(current_device_id),
        },
        "bootstrap": bootstrap,
    }
    save_state(
        value,
        expected_revision=existing_state["revision"] if existing_state is not None else None,
    )
    return {
        "action": "write-state",
        "repository": f"{owner}/{repo}",
        "branch": ref,
        "head_sha": head,
        "device_id": current_device_id,
        "device_branch": device_branch(current_device_id),
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
    if not args.setup:
        raise BackendError("--setup is required for first-run repository creation")
    if load_state() is not None:
        raise BackendError("a local binding already exists; use the explicit rebind flow")
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
    run_gh_command(
        [
            "gh",
            "repo",
            "create",
            f"{owner}/{repo}",
            "--private",
            "--add-readme",
            "--description",
            description,
        ]
    )
    info = gh_api(endpoint(owner, repo))
    if not isinstance(info, dict):
        raise BackendError("repository was created but GitHub returned no repository metadata")
    if info.get("visibility") != "private":
        raise BackendError("repository was created, but its visibility is not private")
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
        "visibility": "private",
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
    _, bound_branch = require_bound_device_state(owner, repo)
    if ref != bound_branch:
        raise BackendError(f"documentation writes must target the bound device branch {bound_branch}")
    message = required_text(args.commit_message, "commit-message")
    if args.expected_head_sha is None:
        raise BackendError("--expected-head-sha is required for every documentation write")
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
    commit_sha = (result or {}).get("commit", {}).get("sha")
    state_update = record_bound_head(owner, repo, ref, commit_sha) if commit_sha else {
        "state_updated": False,
        "state_update_reason": "GitHub returned no commit SHA",
    }
    return {
        "action": "update" if existing is not None else "create",
        "path": path,
        "branch": ref,
        "content_sha": (result or {}).get("content", {}).get("sha"),
        "commit_sha": commit_sha,
        **state_update,
    }


def delete_file(args: argparse.Namespace) -> dict[str, Any]:
    if not args.approved:
        raise BackendError("--approved is required after explicit bounded user approval")
    owner, repo = repository(args.owner, args.repo)
    enforce_personal_repository(owner, repo)
    path = repo_path(args.path)
    ref = branch(args.branch)
    _, bound_branch = require_bound_device_state(owner, repo)
    if ref != bound_branch:
        raise BackendError(f"documentation writes must target the bound device branch {bound_branch}")
    expected = sha(args.expected_sha, "expected-sha")
    if args.expected_head_sha is None:
        raise BackendError("--expected-head-sha is required for every documentation deletion")
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
    commit_sha = (result or {}).get("commit", {}).get("sha")
    state_update = record_bound_head(owner, repo, ref, commit_sha) if commit_sha else {
        "state_updated": False,
        "state_update_reason": "GitHub returned no commit SHA",
    }
    return {
        "action": "delete",
        "path": path,
        "branch": ref,
        "commit_sha": commit_sha,
        **state_update,
    }


def add_repository_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)


def add_ref_args(parser: argparse.ArgumentParser) -> None:
    add_repository_args(parser)
    parser.add_argument("--branch", default="main")


def add_read_scope_args(parser: argparse.ArgumentParser) -> None:
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--setup", action="store_true", help="allow an unbound first-run verification read")
    scope.add_argument("--rebind", action="store_true", help="allow an explicit rebind verification read")


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
    state_write_parser.add_argument("--head-sha", required=True)
    state_write_parser.add_argument("--device-id", required=True)
    state_write_scope = state_write_parser.add_mutually_exclusive_group(required=True)
    state_write_scope.add_argument("--setup", action="store_true")
    state_write_scope.add_argument("--rebind", action="store_true")
    state_write_parser.add_argument("--verified", action="store_true")
    state_write_parser.set_defaults(handler=write_binding)

    device_bind_parser = subparsers.add_parser("bind-device")
    add_repository_args(device_bind_parser)
    device_bind_parser.add_argument("--branch", default="main")
    device_bind_parser.add_argument("--device-id", required=True)
    device_bind_parser.add_argument("--verified", action="store_true")
    device_bind_parser.add_argument("--rebind-device", action="store_true")
    device_bind_parser.add_argument("--approved", action="store_true")
    device_bind_parser.set_defaults(handler=bind_device)

    state_sync_parser = subparsers.add_parser("sync-binding-head")
    add_repository_args(state_sync_parser)
    state_sync_parser.add_argument("--branch", default="main")
    state_sync_parser.add_argument(
        "--activate",
        action="store_true",
        help="initialize a missing local checkpoint from the verified remote branch HEAD",
    )
    state_sync_parser.set_defaults(handler=sync_binding_head)

    info_parser = subparsers.add_parser("repository")
    add_repository_args(info_parser)
    add_read_scope_args(info_parser)
    info_parser.set_defaults(handler=repository_info)

    create_repo_parser = subparsers.add_parser("create-repository")
    add_repository_args(create_repo_parser)
    create_repo_parser.add_argument("--setup", action="store_true")
    create_repo_parser.add_argument(
        "--description",
        default="InfraKeeper infrastructure documentation",
    )
    create_repo_parser.add_argument("--approved", action="store_true")
    create_repo_parser.set_defaults(handler=create_repository)

    commits_parser = subparsers.add_parser("list-commits")
    add_ref_args(commits_parser)
    add_read_scope_args(commits_parser)
    commits_parser.add_argument("--per-page", type=int, default=10)
    commits_parser.set_defaults(handler=list_commits)

    head_parser = subparsers.add_parser("repository-head")
    add_ref_args(head_parser)
    add_read_scope_args(head_parser)
    head_parser.set_defaults(handler=repository_head)

    branch_head_parser = subparsers.add_parser("branch-head")
    add_ref_args(branch_head_parser)
    add_read_scope_args(branch_head_parser)
    branch_head_parser.set_defaults(handler=branch_head)

    device_branches_parser = subparsers.add_parser("list-device-branches")
    add_repository_args(device_branches_parser)
    add_read_scope_args(device_branches_parser)
    device_branches_parser.set_defaults(handler=list_device_branches)

    device_branch_parser = subparsers.add_parser("ensure-device-branch")
    add_repository_args(device_branch_parser)
    device_branch_parser.add_argument("--main-head-sha", required=True)
    device_branch_parser.add_argument("--approved", action="store_true")
    device_branch_parser.set_defaults(handler=ensure_device_branch)

    file_parser = subparsers.add_parser("get-file")
    add_ref_args(file_parser)
    add_read_scope_args(file_parser)
    file_parser.add_argument("--path", required=True)
    file_parser.set_defaults(handler=read_file)

    directory_parser = subparsers.add_parser("list-directory")
    add_ref_args(directory_parser)
    add_read_scope_args(directory_parser)
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
    write_parser.add_argument("--expected-head-sha", required=True)
    write_parser.set_defaults(handler=write_file)

    delete_parser = subparsers.add_parser("delete-file")
    add_ref_args(delete_parser)
    delete_parser.add_argument("--path", required=True)
    delete_parser.add_argument("--commit-message", required=True)
    delete_parser.add_argument("--approved", action="store_true")
    delete_parser.add_argument("--expected-sha", required=True)
    delete_parser.add_argument("--expected-head-sha", required=True)
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
