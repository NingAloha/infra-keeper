# Interactive setup wizard

Guided, **read-only** configuration of GitHub access for a first-time user. This is the entry point
for "初始化 InfraKeeper" / "set up InfraKeeper". It is not a device audit and it never writes
repository content.

## Trigger

Enter this flow when the user asks to initialize, set up, configure, connect or re-check InfraKeeper
or its GitHub access, for example:

- `初始化 InfraKeeper`, `配置 InfraKeeper`, `连接 GitHub`, `添加另一个后端`, `重新验证连接`
- "set up InfraKeeper", "connect GitHub", "add a backend", "re-verify access"

Do not enter it for ordinary documentation work, and do not merge it into an audit run. If the user
asks for an audit before setup, run this flow first: an audit needs a bound repository.

## Safety contract

Setup is read-only, including when the user offers to let you "just test it":

- Probe only with the read operations named below. Never create, modify, move or delete a file, and
  never create a "test" commit or branch. **Zero GitHub writes** for the whole flow, including the
  stages that only prove a connection works.
- Never change the host's MCP configuration, environment variables, shell profiles or credential
  files. **Zero automatic authentication or configuration changes**: give guidance and stop; acting
  on it needs the user's explicit, separate approval in their own environment.
- The user performs OAuth, PAT creation and `gh auth login` themselves. Never ask for, echo, store
  or log a token, code, client secret or password, and never suggest sending one through chat.
- A denial from one backend is final for that operation. Do not retry it on the other backend.
- Never treat this project's own repository as the user's infrastructure repository.
- If a capability cannot be inspected, report `unverified`. Do not guess `ready` or `unavailable`.

## Read scope (hard rule)

Every read must clear the current rung of this ladder before it is made.

| Stage | Reads allowed |
| --- | --- |
| S1 | host capability only: which MCP tools this session exposes, whether a local command may run |
| S3 / S4 | additionally, identity only: which user each backend is authenticated as |
| after S5 names a repository | that repository only: its metadata, its `main`, its contents |
| at any time | nothing about a repository the user has not named |

- Before the user names `OWNER/REPO`, do not enumerate repositories, list an account's repositories,
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
| S0 idle | no setup in progress | user asks to initialize |
| S1 scan | detect host capabilities | always continues |
| S2 select | user chooses backend(s) | at least one backend chosen |
| S3 MCP connection | tool presence, identity, configuration guidance | connection status recorded |
| S4 CLI connection | binary presence, authentication, guidance | connection status recorded |
| S5 bind | obtain `OWNER/REPO`, check `main` and visibility | repository accepted |
| S6 repository verification | read-only probe of that repository, per backend | per-backend status recorded |
| S7 report | readiness table, summary, handoff | setup ends |

Two ordering rules follow from this list:

- **A repository-level verdict requires a repository.** S3 and S4 can only establish whether a
  backend is present, authenticated and configured. `ready` is reserved for S6, after S5 has fixed
  the target. Before that, do not describe any backend as ready for a repository.
- **Guidance may precede binding.** Installation and authentication help in S3/S4 needs no
  repository, so a user who has not chosen one yet can still be walked through setup.

Nothing is persisted between runs: no config file, database or cache. Re-running is **safe** — it
re-probes and reports current facts — but it is not claimed to be strictly idempotent: results can
differ between runs when the host, the identity, the token scopes or the repository change.

## S1 — host capability scan

Two capabilities decide what can be offered:

| Capability | How to check | Possible answers |
| --- | --- | --- |
| GitHub MCP | inspect the tools this session exposes | detected / not detected / cannot inspect |
| Local commands | run one harmless read-only command, if host policy allows | available / policy-denied / unavailable / cannot determine |

Rules:

- A missing tool is not proof of missing permission, and a present tool is not proof of a valid
  identity. S3 resolves both.
- Never claim to have scanned a capability you cannot inspect. Name the check that was impossible
  and continue with what remains.
- Do not install anything, `gh` included, without an explicit request.

## S2 — choose backends

Offer three shapes and let the user pick: MCP only, CLI only, or both. Prefer MCP when it is
detected, otherwise CLI when commands are available. If neither is usable, explain both gaps and
finish at S7 with `unavailable`.

Both backends may be configured, and **each keeps its own status**. They are alternative channels
for an *operation*, never a fallback chain for a *denial*; see "Denials and switching".

## S3 — MCP connection stage

1. If the host exposes no GitHub MCP tool and the tool list cannot be inspected, record `unverified`
   and state that inspection was impossible. If inspection worked and found no such tool, record
   `unavailable`.
2. If tools exist, verify identity only: current user. A `401` records `unauthenticated`. Do not
   read any repository at this stage; see "Read scope".
3. When the backend is not configured, guide — do not configure it for the user:
   - Hosted server endpoint: `https://api.githubcopilot.com/mcp/`.
   - Least privilege is a fine-grained PAT scoped to the target repository with **Contents: Read**
     and **Metadata: Read** (granted automatically). A classic token carrying `repo` grants far
     more; suggest it only if the user accepts that wider scope.
   - The secret belongs in the host's private credential store or an environment variable, never in
     this repository, in a printed shell line, or in the chat.
   - Some hosts need a new session before newly configured tools appear.
   - Verify with the host's own diagnostic (Hermes: `hermes mcp test <name>`), not by attempting a
     write.
4. Record the connection result, for example "identity confirmed; no repository bound yet". Do not
   report `ready` from this stage.

## S4 — CLI connection stage

1. `gh --version`. If the binary is missing, record `unavailable` and point to
   https://cli.github.com/. Do not install it unprompted.
2. `gh auth status`. If it reports no login, record `unauthenticated` and ask the user to run
   `gh auth login` in their own terminal. If they prefer `GH_TOKEN`, it must come from their own
   secure environment; never ask for its value.
3. `gh auth status` prints token scopes; report them if visible, but scopes are neither a repository
   verdict nor permission to write.
4. Record the connection result. Do not report `ready` from this stage.

## S5 — bind the repository

Ask for `OWNER/REPO`. A repository URL or an SSH remote may be accepted and reduced to that pair.

- Confirm `main` exists on that repository using the chosen backend's read operations. If `main`
  does not exist, report it and ask how to proceed — do not create a branch and do not silently
  substitute another one.
- Report the visibility (`public` / `private`), because it constrains what may be committed later.

If the user does not want to bind a repository yet, stop after S3/S4 with connection-level status
and say plainly that no repository has been verified.

If a binding is already stored, show it here and ask whether to re-verify it or to rebind; see
"Repository binding (persisted)".

## S6 — repository verification

Only after S5, and once per selected backend. The minimal probe is repository metadata plus a root
listing of `OWNER/REPO` at `main`; that proves read access and that the bound branch exists.

| Observation | Status | Note |
| --- | --- | --- |
| probe succeeds | `ready` | scope it: "read access to `OWNER/REPO@main`" |
| `401` | `unauthenticated` | identity expired or absent |
| `403` | `insufficient-permissions` | explicit refusal for that resource |
| `404` | `unverified` | ambiguous — see below |
| timeout, DNS failure, `5xx`, uninspectable capability | `unverified` | record the reason |
| repository known not to exist | `unverified` | ask for the correct `OWNER/REPO` |

**`404` is not permission evidence.** It can mean the repository name is wrong, the wrong account is
signed in, the token is not scoped to that repository, the repository is private and invisible to
this identity, or an organization requires SSO authorization. Because a 404 cannot separate these,
record `unverified` and give the checks that would resolve it: confirm the exact `OWNER/REPO`,
confirm the signed-in account, confirm the token's repository selection, check organization SSO, and
try the other already-configured backend **as a separate read of the bound repository** — never as a
retry of a denied write, and never against a different repository.

**Partial success is a normal outcome.** With two backends selected, one may be `ready` and the other
`insufficient-permissions`. Report both honestly. If at least one selected backend completes read
verification of the bound repository, state that setup is usable on that backend and that the other
remains unresolved; the user can continue with the verified backend.

## Repository binding (persisted)

A user has one default infrastructure profile repository, maintained over time; devices are many.

Persist a binding only after S6 returned `ready` on at least one selected backend. A repository whose
selected backends all returned `unverified` is not stored.

A binding is trusted only with that provenance: the user picked the repository in a setup run, and at
least one selected backend reached `ready` on it. A repository name that merely appears in host
memory, in an earlier conversation, or in notes is **not** a binding — ask the user to confirm it,
and verify it through S5/S6 before use.

Keep the record minimal: `repository` and `branch`. Verification time and per-backend status may be
kept as historical observations, never as a permission.

- `repository`: `OWNER/REPO`
- `branch`: the branch that was verified, normally `main`
- optional: `verified_at`, `verified_by`, `status`

Store it with whatever durable facility the host offers — host memory, host configuration, a
host-managed store. Do not write it into the repository, and do not depend on a vendor-specific
memory API. If the host has no durable store, say so and ask for `OWNER/REPO` each session instead.

Reuse: ordinary maintenance tasks use the bound repository directly, without re-running S1–S7 and
without asking for the repository again. The user's current explicit selection, and any exclusion,
always override the stored binding. When the user explicitly asks to initialize or re-verify, show
the stored binding and re-run S6 against it.

Rebind: only on an explicit request. The new repository replaces the old binding only after a fresh
S6 verdict of `ready` on at least one backend; until then the old binding stays as it was.

Failure: if a read of the bound repository returns `401`, `403`, `404` or times out, report the
error as it stands and leave the binding unchanged. The failure may be kept as a historical
observation, but that note must not shorten, filter or soften the report you give the user. Do not
switch to another repository, and do not delete the binding without an instruction.

A binding narrows access; it never widens it. An excluded repository stays unreadable even if bound,
and a binding is not permission to write — every write keeps its own per-change approval.

## S7 — readiness report

End every run with a table and a short summary. One row per selected backend:

| Backend | Status | Evidence | Next action |
| --- | --- | --- | --- |
| GitHub MCP | `ready` | identity plus root listing of `OWNER/REPO@main` | none |
| GitHub CLI | `insufficient-permissions` | `403` reading `OWNER/REPO` contents | request access, then re-verify |

Then print one short, copy-pasteable summary. It must contain no credentials, token fragments,
scopes, host names or anything else sensitive:

```text
InfraKeeper setup — summary
backends selected: mcp, cli
repository: OWNER/REPO (main, private)
mcp: ready            (read access verified)
cli: unverified       (404 reading contents; not permission evidence)
outstanding: cli access; device audit (not implemented in this version)
```

Close with three statements: no repository content was written and no authentication or host
configuration was changed; the bound repository is `OWNER/REPO` on `main`; the next step is a
read-only device audit, which this version does not implement.

## Status vocabulary

| Status | Means | Does not mean |
| --- | --- | --- |
| `ready` | read verification of the bound repository succeeded on this backend (S6 only) | write access, or permission beyond read |
| `unavailable` | the backend is structurally absent: no MCP tool, no `gh` binary | that the user has no GitHub access by another route |
| `unauthenticated` | the backend exists but presents no valid identity (`401`, no login) | that the account lacks repository permission |
| `insufficient-permissions` | authenticated, and a read was explicitly refused (`403`) for that repository | that the token is invalid |
| `unverified` | no verdict at the required scope: not yet bound, ambiguous `404`, uninspectable capability, or an inconclusive error | anything about the backend's real state |

`unverified` is the right answer more often than it feels. Use it whenever the evidence does not
name a cause.

## Denials and switching

- A tool or API denial ends that line of work. Report it, quoting the message.
- Do not re-issue the same operation on the other backend. "MCP refused, so try `gh`" is a bypass,
  not a fallback, and it is prohibited.
- Legitimate switching looks like a missing capability plus a user decision: no MCP tool exposed, or
  `gh` not installed, and the user picks the other backend. Record the reason.

## Re-running, resuming, re-verification

Re-running is safe because nothing is stored and every question is answered by a fresh read.

| Situation | Behaviour |
| --- | --- |
| User stops mid-flow | nothing is saved; say so and stop |
| Re-run after interruption | start at S1, report current facts, skip installation guidance for backends already present |
| Add a second backend later | run S1, then only the new backend's path, then S6 for that backend |
| Re-verify a connection | re-run S3/S4 and S6 for the bound repository |
| Target repository changes | restart at S5 with the new `OWNER/REPO` |

## Never in this flow

- No file writes, branches, pull requests or commits, including "test" commits.
- No edits to host configuration, environment or credential files.
- No credential values in output, logs or diffs, including in the S7 summary.
- No assumption that this repository is the user's infrastructure repository.
- No `ready` verdict without a bound repository and a successful read of it.
