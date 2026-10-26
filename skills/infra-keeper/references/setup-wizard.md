# Interactive setup wizard

Automatic preflight and guided configuration of GitHub CLI access. The flow is **read-only for GitHub
after the personal repository is bootstrapped**. On the first run with no stored binding, it may
create exactly one personal repository after a separate approval; later runs only verify that
binding. It runs before the first relevant InfraKeeper task in a new agent session, and is also the
entry point for "初始化 InfraKeeper" / "set up InfraKeeper". It detects
whether `gh` is available, walks the user through installation and authentication one step at a
time, and then creates or verifies the personal repository.

## Trigger

Enter this flow automatically before the first relevant InfraKeeper task in a new agent session, or
when the user explicitly asks to initialize, set up, configure, connect or re-check InfraKeeper or
its GitHub access, for example:

- `初始化 InfraKeeper`, `配置 InfraKeeper`, `连接 GitHub CLI`, `重新验证连接`
- "set up InfraKeeper", "connect GitHub CLI", "re-verify access"

Do not wait for an initialization phrase. Do not enter it for unrelated work, and do not merge it
into an audit run. If the user asks for an audit before the preflight is ready, run this flow first:
an audit needs a bound repository.

## Safety contract

Setup is read-only for GitHub except for the one-time personal-repository bootstrap, including when
the user offers to let you "just test it". An approved local package installation, the approved
repository bootstrap, the non-secret local binding-state write after S5 and a proven fast-forward
refresh of the local checkpoint are the only setup-time mutations allowed by this flow:

- Probe only with the read operations named below. Never create, modify, move or delete a file, and
  never create a "test" commit or branch. There are zero GitHub writes unless this is the first run
  with no binding and the user separately approves creation of the named personal repository.
- Never change the host's environment variables, shell profiles or credential files. The only local
  file this flow may write is the app-owned binding state after S5 or its `main` branch checkpoint after a proven
  fast-forward; it contains no token, credential data or repository contents. **No silent
  installation or authentication**: if the user explicitly asks the assistant to install `gh`, show
  the exact command, package source and expected effect first, obtain separate approval for that
  one command, execute only that command in the Agent page when the host allows it, and re-check
  afterward. A host's own command-approval prompt must also be accepted. Do not hide a package
  manager, login command or repository-creation command inside another operation.
- Prefer keeping the whole flow in the Agent page. Fall back to the user's terminal only when the
  host cannot execute local commands, cannot provide an interactive terminal, or denies the command.
  The user may run `gh auth login` themselves, or separately approve the assistant starting that
  exact interactive command in the Agent page. The user completes the browser/device authorization.
  Never ask for, echo, store or log a token, code, client secret, password or credential-file
  contents, and never suggest sending one through chat.
- A denial from the CLI is final for that operation. Do not retry it through another channel.
- Never treat this project's own repository as the user's infrastructure repository.
- If a capability cannot be inspected, report `unverified`. Do not guess `ready` or `unavailable`.

## Automatic preflight before conversation

Before asking the user for setup information, run these checks in the Agent page when local command
execution is available:

1. Read the local state with `gh_backend.py read-state`.
2. Run `gh --version` and `gh auth status`; report only redacted readiness facts.
3. If a valid local binding exists, verify only that `OWNER/REPO@main` and its root listing are readable,
   and compare GitHub's `main` commit graph with the stored `branches.main` checkpoint. If the remote HEAD
   is a normal descendant, refresh that checkpoint and continue; otherwise report the change and stop writes. If
   a device branch is bound, read its HEAD too; do not create or modify it during preflight.
4. If no valid binding exists, report the scan result and then ask for a repository name. The default is
   `infrastructure`; no repository is enumerated or guessed.

This preflight does not create a repository, install packages, start login, or change binding metadata.
It may only refresh the `main` branch checkpoint after proving that GitHub `main` is a normal descendant of the stored
checkpoint. All other local-state writes and all GitHub writes still use the approval gates below. A
successful preflight may be summarized before the agent continues with the user's requested task.

## Read scope (hard rule)

Every read must clear the current rung of this ladder before it is made.

| Stage | Reads allowed |
| --- | --- |
| before S1 / at any time | the app-owned local binding state only |
| S1 | host capability only: whether a local command may run |
| S3 | additionally, identity only: which user the local CLI is authenticated as |
| after S4 names a candidate | that candidate only: existence/metadata; after creation, its `main` and contents |
| at any time | nothing about a repository the user has not named |

- Before the user names `OWNER/REPO` or a valid local binding identifies it, do not enumerate repositories, list an account's repositories,
  search code, or read any repository's contents, branches or metadata. "Discover accessible
  repositories" is a rule for documentation work; it does not apply to this flow.
- After binding, read only the bound repository. Do not read a second repository to compare, to
  calibrate, or to demonstrate that the first one is reachable.
- If the user names a repository as off-limits, record it as excluded and never read it again — not
  for diagnostics, not as an example, not as a substitute target, not to check whether access works.
- An ambiguous `404` is resolved by reasoning and by asking, not by reading more. Restate the exact
  name the user gave, restate which identity is authenticated, and ask them to confirm. Reading some
  other repository to infer the cause is prohibited.
- A failed read is never a reason to read something else.
- If the flow needs an answer and no interactive channel exists, stop and say which question is
  missing. Do not pick a default repository, and do not read anything to compensate for the missing
  answer.

## Language

Answer in the language the user is using.

1. An explicit user statement wins for the rest of the flow: "reply in Chinese", `用英文回答`.
2. Otherwise use the language of the request that started setup: a Chinese trigger gets Chinese
   guidance, an English trigger gets English guidance.
3. Do not infer a language from the user's profile, memory, other sessions, or documents they wrote
   earlier.

Language changes wording only. States, verdicts, safety rules and refusal behaviour stay identical
in both languages.

## States

| State | Purpose | Exit |
| --- | --- | --- |
| S0 idle | no setup in progress | first relevant task or explicit setup request |
| S1 scan | detect host capabilities | always continues |
| S2 select | confirm the CLI path | CLI selected or unavailable |
| S3 CLI connection | binary presence, authentication, guidance | connection status recorded |
| S4 create or bind | obtain a personal `OWNER/REPO`; create once or re-verify an existing binding | repository created or accepted |
| S5 repository verification | read-only probe of that repository | readiness status recorded |
| S6 report | readiness table, summary, handoff | setup ends |

Two ordering rules follow from this list:

- **A repository-level verdict requires a repository.** S3 can only establish whether the CLI is
  present and authenticated. `ready` is reserved for S5, after S4 has fixed or created the target. Before that,
  do not describe the CLI as ready for a repository.
- **Guidance may precede binding.** Installation and authentication help in S3 needs no
  repository, so a user who has not chosen one yet can still be walked through setup.

After S5, persist only the binding metadata in the app-owned local state file. Re-running is **safe** —
it reads that state and re-probes the current identity and repository — but it is not claimed to be
strictly idempotent: results can differ between runs when the host, the identity, the token scopes or
the repository change. If the state file is missing or invalid, ask for the repository again; never
guess from another repository.

## S1 — host capability scan

The only capability that decides whether setup can continue is local command execution:

| Capability | How to check | Possible answers |
| --- | --- | --- |
| Local commands | run one harmless read-only command, if host policy allows | available / policy-denied / unavailable / cannot determine |
| Interactive local commands | determine whether the Agent page can keep a command interactive | available / policy-denied / unavailable / cannot determine |

Rules:

- A runnable command is not proof of a valid GitHub identity. S3 resolves authentication.
- Never claim to have scanned a capability you cannot inspect. Name the check that was impossible.
- The setup request authorizes installation guidance, not an unattended package-manager mutation.
- Prefer the Agent page when local command execution and the required interactivity are available;
  otherwise report the capability gap and offer the user's terminal as a fallback.

## S2 — choose the CLI path

There is one backend: local GitHub CLI. If local commands are unavailable or policy-denied, explain
the gap and finish at S6 with `unavailable`. The bundled JSON helper and direct `gh` commands share
the same identity; the helper is preferred when it can run.

## S3 — CLI detection, installation guidance and authentication

Run this stage as a checkpointed loop. Never assume that a command succeeded because the user said
they intended to run it; re-probe after each completed step.

1. Run `gh --version`.
2. If `gh` is missing, report `unavailable`, ask which operating system the user is using if it is
   not known, and give one installation path:
   - macOS with Homebrew: `brew install gh`
   - Windows with WinGet: `winget install --id GitHub.cli`
   - Linux or another environment: use the official installation page at
     https://cli.github.com/ or https://github.com/cli/cli#installation
3. Prefer running the installation in the Agent page. Show a confirmation like this before executing
   anything:

   ```text
   即将执行：brew install gh
   来源：Homebrew 的 GitHub CLI 包
   影响：在本机安装 GitHub CLI；不会登录 GitHub，也不会修改仓库
   是否批准仅执行这条命令？
   ```

   After explicit approval, execute exactly the shown package-manager command once in the Agent page.
   Do not add a package source, modify a shell profile, use `curl | sh`, or silently add `sudo`. If
   the Agent page cannot provide the required terminal interaction, stop and give the same command
   for the user to run locally. For Linux or another environment, do not invent a distro command:
   use the official instructions or ask the user to provide the exact command they want approved.
4. After the user-run or approved assistant-run installation finishes, re-run `gh --version`. A prior
   `unavailable` result must not be reused after installation.
5. Once the binary is present, run `gh auth status`. If it reports no login, prefer starting
   `gh auth login` in the Agent page after showing the exact command and requesting separate approval.
   The user completes the browser or device authorization. If the Agent page cannot keep the
   interactive login usable, provide the command as a terminal fallback. For GitHub Enterprise, use
   `gh auth login --hostname HOST` with the user's own host name.
6. Re-run `gh auth status` after the user reports completion. Never ask for or echo a token, password,
   one-time code or credential-file contents. If the user prefers `GH_TOKEN`, it must come from their
   own secure environment.
7. `gh auth status` may expose token scopes; report only the minimum relevant redacted status. Scopes
   are neither a repository verdict nor permission to write.
8. Record the connection result. Do not report `ready` from this stage; `ready` is reserved for S5.

The expected conversational checkpoints are:

```text
Agent 页面检测 gh → 展示命令并请求批准 → Agent 页面执行
       → 重新检测 gh → Agent 页面单独批准 gh auth login → 用户完成浏览器授权
       → 若宿主不支持，再退回用户终端执行
       → 重新检测登录 → 用户提供 OWNER/REPO → 只读验证仓库
```

## S4 — create or bind the personal repository

At the start of setup, read the local binding state. If a valid binding is stored, show it here and
re-verify it; do not ask for a new name or attempt to create another repository. See "Repository
binding (persisted)". If the state is missing or invalid, continue with first-run name selection.

If no binding exists, ask for a repository name. The default suggestion is `infrastructure`, and the
full target is the authenticated user's `OWNER/infrastructure`. The user may choose another name.

1. Compare the target owner case-insensitively with the login verified in S3. A different owner is
   `out-of-scope`; do not read or create organization, collaborator or another user's repositories.
2. Check whether `OWNER/REPO` already exists. If it exists, do not bind it and do not overwrite it;
   ask the user for a different unused name. If the check is denied or ambiguous, stop instead of
   guessing that the name is available.
3. If the name is unused, show the one-time creation plan:

   ```text
   Repository: OWNER/REPO
   Visibility: private
   Initial content: README.md
   Branch requirement: main
   Effect: create one new personal GitHub repository and its initial commit
   ```

   Ask for separate approval to create exactly this repository. This is the only repository-creation
   approval in setup. Visibility is always private; there is no public-repository setup path.
4. After approval, run the bundled `create-repository` helper, which invokes
   `gh repo create OWNER/REPO --private --add-readme`. Do not create a branch, add a remote, clone,
   push local content, or modify repository settings as part of bootstrap.
5. Read back repository metadata. If the created repository does not have `main`, report the partial
   result and stop; do not create or rename a branch automatically.
6. Report the visibility and continue to S5 for the root read. Only a successful S5 result creates
   the stored binding. After S5, write the local state atomically with the verified repository,
   `main`, the verified HEAD SHA, and bootstrap status (`created` for this path plus the initial commit
   SHA; `reused` for an existing binding). Ask for a stable device ID before writing the binding; the
   device branch is derived as `infra/device/<device-id>` and is created only with the first approved
   documentation task. A failure to write local state does not change the GitHub verdict, but must be
   reported because the next session may ask for the repository again.

## S5 — repository verification

Only after S4. The minimal probe is repository metadata, the `main` HEAD SHA and a root listing of
`OWNER/REPO` at `main`; that proves read access, identifies the exact branch version and confirms that
the bound branch exists.

| Observation | Status | Note |
| --- | --- | --- |
| probe succeeds and HEAD matches the checkpoint | `ready` | scope it: "read access to `OWNER/REPO@main`" |
| probe succeeds and remote HEAD is a normal descendant | `ready` | refresh local `branches.main`, report the fast-forward and continue |
| probe succeeds but remote HEAD is behind, diverged or rewritten | `changed-since-state` | report both SHAs and the comparison result; stop automatic writes |
| `401` | `unauthenticated` | identity expired or absent |
| `403` | `insufficient-permissions` | explicit refusal for that resource |
| `404` | `unverified` | ambiguous — see below |
| timeout, DNS failure, `5xx`, uninspectable capability | `unverified` | record the reason |
| repository known not to exist | `unverified` | ask for the correct `OWNER/REPO` |

**`404` is not permission evidence.** It can mean the repository name is wrong, the wrong account is
signed in, the token is not scoped to that repository, the repository is private and invisible to
this identity, or an organization requires SSO authorization. Because a 404 cannot separate these,
record `unverified` and give the checks that would resolve it: confirm the exact `OWNER/REPO`,
confirm the signed-in account, confirm the token's repository selection, and check organization SSO.

## Repository binding (persisted)

A user has one default infrastructure profile repository, maintained over time; devices are many.

Persist a binding only after S5 returned `ready` for the CLI. A repository whose verification is
`unverified` is not stored.

A binding is trusted only with that provenance: the user picked or approved creation of the repository
in a setup run, and the CLI reached `ready` on it. A repository name that merely appears in host
memory, in an earlier conversation, or in notes is **not** a binding — ask the user to confirm it, and
verify it through S4/S5 before use.

Keep the record minimal and non-secret. The bundled helper stores a versioned JSON object containing:

```json
{
  "version": 4,
  "binding": {
    "repository": "OWNER/REPO",
    "branch": "main",
    "branches": {"main": "...", "infra/device/laptop": "..."},
    "device_id": "laptop",
    "device_branch": "infra/device/laptop"
  },
  "bootstrap": {"status": "created", "initial_commit_sha": "..."}
}
```

For a reused existing binding, `bootstrap.status` is `reused` and the initial SHA may be absent.

- `repository`: `OWNER/REPO`
- `branch`: the canonical branch that was verified, always `main`
- `branches`: map each tracked branch to its latest verified HEAD SHA; `main` is the default checkpoint
  and is refreshed on every session
- `device_id`: the stable user-provided identifier for this device
- `device_branch`: the only branch this device may write, derived as `infra/device/<device-id>`
- device branch entries are activated and refreshed only when the current task discusses that device

Store it in the bundled helper's app-owned local state file. On macOS this is under
`~/Library/Application Support/InfraKeeper/state.json`; on Windows it is under the user's
`LOCALAPPDATA\InfraKeeper\state.json`; on Linux and other Unix-like systems it is under
`$XDG_STATE_HOME/infra-keeper/state.json` or `~/.local/state/infra-keeper/state.json`. Do not write
it into the repository, and do not store tokens, `gh` credentials or repository contents. If the host
does not allow this file to be read or written, say so and ask for `OWNER/REPO` each session instead. A
state file without a `branches.main` checkpoint is upgraded after a successful fresh S5 verification.

Reuse: ordinary maintenance tasks use the bound repository directly, without re-running S1–S6 and
without asking for the repository again. The user's current explicit selection, and any exclusion,
always override the stored binding. When the user explicitly asks to initialize or re-verify, show
the stored binding and re-run S5 against it.

Rebind: only on an explicit request. A rebind may select an already-existing personal repository after
fresh S4/S5 verification, but it must not silently create another repository. The new repository
replaces the old binding only after a fresh S5 verdict of `ready` for the CLI; until then the old
binding stays as it was.

Failure: if a read of the bound repository returns `401`, `403`, `404` or times out, report the
error as it stands and leave the binding unchanged. The failure may be kept as a historical
observation, but that note must not shorten, filter or soften the report you give the user. Do not
switch to another repository, and do not delete the binding without an instruction.

A binding narrows access; it never widens it. An excluded repository stays unreadable even if bound,
and a binding is not permission to write — every write keeps its own per-change approval.

## S6 — readiness report

End every run with a table and a short summary for the CLI path:

| Backend | Status | Evidence | Next action |
| --- | --- | --- | --- |
| GitHub CLI | `ready` | identity plus root listing of `OWNER/REPO@main`; device branch binding recorded | none |

Then print one short, copy-pasteable summary. It must contain no credentials, token fragments,
scopes, host names or anything else sensitive:

```text
InfraKeeper setup — summary
backend selected: cli
repository: OWNER/REPO (main, private)
device branch: infra/device/DEVICE_ID
cli: ready            (read access verified)
bootstrap: created in this run / reused existing binding
```

Close with three statements: no repository content was changed during setup after bootstrap; branch,
documentation and device-branch writes belong only to a later explicitly approved task; if this was the first
run, report the exact repository-creation command and resulting initial commit separately; any
approved local installation or login command is also reported separately, the local state file was
written (or why it could not be written), and no other host configuration was changed; the bound
repository is `OWNER/REPO` on canonical `main`; device-specific writes use `infra/device/DEVICE_ID`; the requested work can now continue.

## Status vocabulary

| Status | Means | Does not mean |
| --- | --- | --- |
| `ready` | read verification of the bound repository succeeded on the CLI (S5 only) | write access, or permission beyond read |
| `changed-since-state` | GitHub `main` is not a normal descendant of the local binding checkpoint | that the change is unauthorized; investigate the reported comparison |
| `unavailable` | the CLI is absent or local command execution is unavailable | that the user has no GitHub access by another route |
| `unauthenticated` | the CLI exists but presents no valid identity (`401`, no login) | that the account lacks repository permission |
| `insufficient-permissions` | authenticated, and a read was explicitly refused (`403`) for that repository | that the token is invalid |
| `out-of-scope` | the requested repository owner does not match the authenticated user's login | that the repository does not exist |
| `unverified` | no verdict at the required scope: not yet bound, ambiguous `404`, uninspectable capability, or an inconclusive error | anything about the backend's real state |

`unverified` is the right answer more often than it feels. Use it whenever the evidence does not
name a cause.

## Denials and switching

- A tool or API denial ends that line of work. Report it, quoting the message.
- Do not re-issue the same operation through another channel. A CLI refusal is a stop condition,
  not a reason to try a different integration.

## Re-running, resuming, re-verification

Re-running is safe because only non-secret binding metadata is stored and every GitHub question is
answered by a fresh read.

| Situation | Behaviour |
| --- | --- |
| User stops mid-flow | do not write binding state; say so and stop |
| Re-run after interruption | start at S1, report current facts, skip installation guidance for backends already present |
| Re-verify a connection | re-run S3 and S5 for the bound repository |
| Target repository changes | restart at S4 with the new `OWNER/REPO` |

## Never in this flow

- No repository file or branch writes during setup after bootstrap. The only
  setup-time GitHub write is the first-run `gh repo create --add-readme` operation explicitly approved
  for the new repository; later documentation tasks use the device-branch workflow.
- No edits to host configuration, environment or credential files; the only local write is the
  app-owned, non-secret binding state after successful S5.
- No credential values in output, logs or diffs, including in the S6 summary.
- No assumption that this repository is the user's infrastructure repository.
- No `ready` verdict without a bound repository and a successful read of it.
