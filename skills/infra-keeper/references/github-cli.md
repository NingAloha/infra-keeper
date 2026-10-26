# GitHub CLI backend (`gh`)

Official manual: https://cli.github.com/manual/

Use this backend only when the Agent has authorized local command execution and GitHub CLI is installed and authenticated. This is the only GitHub backend provided by this version of InfraKeeper. The target repository must be owned by the authenticated GitHub user; organization and other-user repositories are out of scope.

## Readiness

```sh
gh --version
gh auth status
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef
```

If not authenticated, tell the user to authenticate in their own terminal using `gh auth login` or their host's secure credential mechanism; **never ask them to paste access tokens in chat or commit them**. Check actual repository access with the chosen identity; a successful login alone does not imply write permission. `GH_TOKEN` is supported for noninteractive environments, but credentials must come from a secure external source.

## Bundled JSON CLI helper

When the host can execute packaged scripts, prefer:

```sh
python3 skills/infra-keeper/scripts/gh_backend.py authenticated-user
python3 skills/infra-keeper/scripts/gh_backend.py read-state
python3 skills/infra-keeper/scripts/gh_backend.py repository-head --owner OWNER --repo REPO --branch main
python3 skills/infra-keeper/scripts/gh_backend.py sync-binding-head --owner OWNER --repo REPO --branch main
# only when the current task discusses an existing device branch
python3 skills/infra-keeper/scripts/gh_backend.py sync-binding-head --owner OWNER --repo REPO --branch infra/device/DEVICE_ID --activate
python3 skills/infra-keeper/scripts/gh_backend.py bind-device --owner OWNER --repo REPO --device-id DEVICE_ID --verified
python3 skills/infra-keeper/scripts/gh_backend.py ensure-device-branch --owner OWNER --repo REPO --main-head-sha MAIN_HEAD_SHA --approved
python3 skills/infra-keeper/scripts/gh_backend.py repository --owner OWNER --repo REPO
python3 skills/infra-keeper/scripts/gh_backend.py create-repository --owner OWNER --repo REPO --setup --approved
python3 skills/infra-keeper/scripts/gh_backend.py write-binding --owner OWNER --repo REPO --branch main --bootstrap-status created --initial-commit-sha INITIAL_SHA --head-sha HEAD_SHA --device-id DEVICE_ID --setup --verified
python3 skills/infra-keeper/scripts/gh_backend.py get-file --owner OWNER --repo REPO --path README.md --branch main
python3 skills/infra-keeper/scripts/gh_backend.py list-directory --owner OWNER --repo REPO --branch main
python3 skills/infra-keeper/scripts/gh_backend.py list-commits --owner OWNER --repo REPO --branch main
```

The helper calls `gh api` without a shell, emits machine-readable JSON, validates repository paths,
requires the requested repository owner to match the authenticated user's GitHub login, and keeps
credentials in `gh`'s own credential mechanism. Its `create-repository` command is only for the
first-run bootstrap, always creates a private repository with `--add-readme`, and requires `--setup` plus
`--approved`. Ordinary reads must match the local binding; `--setup` and `--rebind` are the only
verification-read exceptions. `write-binding` likewise requires an explicit `--setup` or `--rebind` mode.
Its `read-state`, `write-binding` and `bind-device` commands manage only the local
non-secret binding state. `repository-head` reads a branch HEAD. `sync-binding-head` compares the stored
checkpoint for the requested branch with GitHub's commit graph and updates local state only when the
remote branch is a normal descendant; it returns `changed-since-state` without updating state for a
rewind, divergence or history rewrite. `bind-device` records the device-local branch identity, and
`ensure-device-branch` creates only that branch after task approval. Write the initial binding only after
the repository metadata, `main` HEAD and root listing have passed S5; `--verified` is a required guard.
The state file is local to the host and is not committed to GitHub. It supports `create-or-update-file` and
`delete-file` only with `--approved`; updates require `--expected-sha`, deletes always require a
matching `--expected-sha`, and both can check `--expected-head-sha`. Use a temporary content file for
larger approved documents rather than putting sensitive values in command arguments.

The helper is an execution aid, not a second authorization layer. The Skill must still establish
the exact approved path, content/diff, impact and rollback before passing `--approved`.

Use `sync-binding-head --branch main` during every session preflight. When the current task discusses a
device, activate only that device's checkpoint with
`sync-binding-head --branch infra/device/DEVICE_ID --activate` when the branch already exists. A missing
device branch must be created through the approved `ensure-device-branch` flow; do not activate arbitrary
branches or synchronize every device branch during preflight.

## Read operations (no mutation)

```sh
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef
gh api repos/OWNER/REPO/contents/README.md -f ref=main --method GET
gh api repos/OWNER/REPO/commits?sha=main --method GET
gh api repos/OWNER/REPO/git/trees/main -f recursive=1 --method GET
```

Use `gh api` or the bundled helper for repository reads and inspect returned data carefully. Before a direct `gh` fallback, run `gh api user`, compare its `login` with the requested `OWNER`, and stop on a mismatch. Avoid printing authentication headers, sensitive URLs, or secret-bearing raw logs. Check whether the repository actually has a `main` branch before proceeding.

## Version preconditions (measured)

The Contents API is the version-aware path on this backend. One manual CLI lifecycle test measured
its behaviour on a public repository:

- `PUT /repos/{owner}/{repo}/contents/{path}` requires `sha` to replace an existing file. A stale
  value was rejected with `HTTP 409` and a body naming the supplied SHA; no commit, no new `HEAD`
  and no byte change resulted. A matching value was accepted and produced the expected commit.
- `DELETE` on the same path requires `sha` for the file being deleted, and a delete carrying a
  matching value succeeded.

The rejection came from GitHub itself: the response carried `Server: github.com` and a GitHub
request ID, so on this endpoint the comparison is enforced by the server that creates the commit,
not only by the client.

What was **not** measured: whether a stale `sha` is also rejected on `DELETE`. Only the matching
case was run, because a failed assertion there would remove a path. Do not present the `PUT`
result as if it covered deletes, and do not treat a matching-value delete as proof that a stale
one would be refused.

## Writes: approval first

For an approved documentation change, use the bundled helper so commits are created directly on the
active device branch through `gh`. These commands are **illustrative**, not unattended commands:

```sh
# read navigation on canonical main and ensure the active device branch
python3 skills/infra-keeper/scripts/gh_backend.py get-file --owner OWNER --repo REPO --path README.md --branch main
python3 skills/infra-keeper/scripts/gh_backend.py ensure-device-branch --owner OWNER --repo REPO --main-head-sha MAIN_HEAD_SHA --approved
# read the approved file from the active device branch before preparing its update
python3 skills/infra-keeper/scripts/gh_backend.py get-file --owner OWNER --repo REPO --path path/to/approved-file.md --branch DEVICE_BRANCH
# create or update only on the device branch after approval and SHA checks
python3 skills/infra-keeper/scripts/gh_backend.py create-or-update-file --owner OWNER --repo REPO --branch DEVICE_BRANCH --path path/to/approved-file.md --content-file /tmp/approved-file.md --commit-message "docs: update approved infrastructure record" --approved --expected-head-sha DEVICE_HEAD_SHA --expected-sha FILE_SHA
```

The helper updates the local checkpoint for the active device branch after a successful branch write.
The canonical `main` checkpoint is updated only by the normal session preflight. If the active branch or
file SHA changes during preparation, stop and reassess. Verify the final branch contents through GitHub
reads after the write.

Alternatively, a client may use approved direct `gh api` GitHub Contents API or Git Tree/Commit API
calls, but must respect version SHA preconditions and partial-update risks. See [Version preconditions (measured)](#version-preconditions-measured)
for what has actually been observed on this endpoint and what has not. Never encode secret values into
shell command arguments, files or logs.

## Restrictions

The following are disabled by InfraKeeper policy even if `gh` could execute them: repositories owned by
an organization, a collaborator, or another user; creating a second repository after bootstrap;
arbitrary branch lifecycle, force pushes, history rewriting, repository settings/visibility changes,
and privilege escalation. The bound device branch and its task-scoped creation is the only branch
lifecycle exception. The only repository-creation
exception is the first-run personal private bootstrap described above. If GitHub or the tool host blocks a write,
**stop**; do not try another backend to bypass the rejection.

Official references:
- https://cli.github.com/manual/gh_auth_status
- https://cli.github.com/manual/gh_api
- https://cli.github.com/manual/gh_repo_view
