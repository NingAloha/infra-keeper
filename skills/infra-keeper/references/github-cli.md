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
python3 skills/infra-keeper/scripts/gh_backend.py repository --owner OWNER --repo REPO
python3 skills/infra-keeper/scripts/gh_backend.py create-repository --owner OWNER --repo REPO --approved
python3 skills/infra-keeper/scripts/gh_backend.py get-file --owner OWNER --repo REPO --path README.md --branch main
python3 skills/infra-keeper/scripts/gh_backend.py list-directory --owner OWNER --repo REPO --branch main
python3 skills/infra-keeper/scripts/gh_backend.py list-commits --owner OWNER --repo REPO --branch main
```

The helper calls `gh api` without a shell, emits machine-readable JSON, validates repository paths,
requires the requested repository owner to match the authenticated user's GitHub login, and keeps
credentials in `gh`'s own credential mechanism. Its `create-repository` command is only for the
first-run bootstrap, defaults to a private repository with `--add-readme`, and requires `--approved`.
It supports `create-or-update-file` and
`delete-file` only with `--approved`; updates require `--expected-sha`, deletes always require a
matching `--expected-sha`, and both can check `--expected-head-sha`. Use a temporary content file for
larger approved documents rather than putting sensitive values in command arguments.

The helper is an execution aid, not a second authorization layer. The Skill must still establish
the exact approved path, content/diff, impact and rollback before passing `--approved`.

## Read operations (no mutation)

```sh
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef
gh api repos/OWNER/REPO/contents/README.md -f ref=main --method GET
gh api repos/OWNER/REPO/commits?sha=main --method GET
gh api repos/OWNER/REPO/git/trees/main -f recursive=1 --method GET
```

Use `gh api` or permitted local read-only Git commands where appropriate; inspect returned data carefully. Before a direct `gh` fallback, run `gh api user`, compare its `login` with the requested `OWNER`, and stop on a mismatch. Avoid printing authentication headers, sensitive URLs, or secret-bearing raw logs. Check whether the repository actually has a `main` branch before proceeding.

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

For an approved documentation change, prefer a local checked-out repository and ordinary *non-force* commits when the working tree and branch are known. These are **illustrative**, not unattended commands:

```sh
git status --short
git branch --show-current
git fetch origin main
git status --porcelain
# review the approved diff and confirm the current main has not changed
git diff --check
git diff -- path/to/approved-file.md
# stage only explicitly approved paths; commit and push only after approval
git add -- path/to/approved-file.md
git commit -m "docs: update approved infrastructure record"
git push origin main
```

Do not run `git add -A`, `git push --force`, or commit unrelated local changes. If the tree is dirty, `main` differs from the expected upstream, or a concurrent update occurs, stop and reassess. Verify remote files and the final commit via GitHub read operations after pushing.

Alternatively, a client may use approved `gh api` GitHub Contents API or Git Tree/Commit API calls, but must respect version SHA preconditions and partial-update risks. See [Version preconditions (measured)](#version-preconditions-measured) for what has actually been observed on this endpoint and what has not. Never encode secret values into shell command arguments, files or logs.

## Restrictions

The following are disabled by InfraKeeper policy even if `gh` could execute them: repositories owned by
an organization, a collaborator, or another user; creating a second repository after bootstrap;
branch creation/deletion, pull requests, force pushes, history rewriting, repository
settings/visibility changes, and privilege escalation. The only repository-creation exception is the
first-run personal private bootstrap described above. If GitHub or the tool host blocks a write,
**stop**; do not try another backend to bypass the rejection.

Official references:
- https://cli.github.com/manual/gh_auth_status
- https://cli.github.com/manual/gh_api
- https://cli.github.com/manual/gh_repo_view
