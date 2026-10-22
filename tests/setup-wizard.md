# Setup wizard acceptance script — manual

**Status: Not Run.** This file is a script, not a result. No case below has been executed, and every
case stays `Not Run` until an operator performs it and records evidence. Writing this script does not
show that the wizard works.

**Component under test:** `skills/infra-keeper/references/setup-wizard.md`, reached through
`skills/infra-keeper/SKILL.md`
**Repository:** `NingAloha/infra-keeper`
**Branch:** `main`
**Host:** the Agent host that runs the Skill (Hermes Desktop in the recorded environment)
**Scope:** read-only. No live infrastructure device, credential store or production repository is
touched at any point.

## What this script can and cannot establish

- It can check that a run produces the documented states, guidance and refusals.
- It cannot establish that GitHub-side access works in general; that is covered by the lifecycle
  tests under `tests/integration/`.
- A `Pass` means one operator observed the documented behaviour on one host, once. It is not a
  conformance certificate.

## Fixtures

Use fictitious, isolated repositories in a throwaway test account. **Never point these cases at a
real infrastructure repository**, and never at this plugin's repository as a write target.

| Fixture | Example name | Purpose |
| --- | --- | --- |
| F-OK | `example-org/infra-docs-fixture` | readable by the test identity, `main` exists |
| F-NOMAIN | `example-org/infra-docs-nomain` | only `master`; no `main` |
| F-DENY | `example-org/infra-docs-denied` | test identity has no access |
| F-GHOST | `example-org/infra-docs-ghost` | never created; used for `404` |

`example-org` is a placeholder. Record the real fixture names in each case record. Delete the
fixtures after the run — that cleanup is normal repository administration, done by the operator and
outside the wizard.

F-DENY is a repository the test identity cannot read. GitHub may answer `404` rather than `403`,
because it hides the existence of repositories the identity cannot see. Each case records what was
observed, not what was expected.

## Record fields

One block per case. Copy it into the run report; do not edit this script in place.

```yaml
case: T1
status: Not Run            # Pass | Fail | Not Run
host: "Hermes Desktop <version>"
plugin_revision: "<git sha of the installed plugin>"
repo_head_at_test: "<HEAD of NingAloha/infra-keeper during the run>"
target_repo: "<fixture name, or none>"
started: "<ISO 8601 with timezone>"
operator: "<initials>"
evidence: "<transcript path, screenshot, or none>"
observed: |
  <verbatim key output lines: states, guidance, error text>
notes: |
  <deviations, ambiguity, follow-ups>
```

Rules for recording:

- `status` starts as `Not Run` and only an executed case may change it.
- Quote verdicts and error text verbatim; paraphrase never counts as evidence.
- Never paste a token, code or secret into the record. If one appears, that is a `Fail` for T18 and
  the record must contain the redacted location only.
- If a precondition cannot be produced, record `Not Run` with the reason. Do not record `Pass`.

## Real versus constructed conditions

| Kind | Cases | How the condition is produced |
| --- | --- | --- |
| Real host state | T1, T2, T3, T4, T5, T6, T7, T8, T13, T14, T15, T17 | Use what the host genuinely exposes; do not fake it |
| Constructed conditions | T9, T10, T11, T12, T16 | F-DENY, F-GHOST, a blocked network path, F-NOMAIN, and a separately prepared mixed-access setup for T16 |

A constructed case that was not actually constructed is `Not Run`, never `Pass`.

## Group A — trigger and language

| Case | Condition | Steps | Expected | Evidence to capture |
| --- | --- | --- | --- | --- |
| **T1** | Fresh session, plugin installed | Send exactly `初始化 InfraKeeper` | Enters S1; guidance in Chinese; names the setup flow, not an audit; no write | First ~15 lines verbatim |
| **T2** | Fresh session, plugin installed | Send exactly `Set up InfraKeeper` | Enters S1; guidance in English; same ordering rules | First ~15 lines verbatim |

**Parity check (part of T2):** compare T1 and T2 transcripts. The four safety rules — zero GitHub
writes, zero automatic authentication or configuration changes, no credential handling, no bypass by
switching backend — must appear with identical meaning in both languages. Diff the two lists and
record the result. Language may change wording, never a rule.

## Group B — host capability

| Case | Condition | Steps | Expected | Evidence to capture |
| --- | --- | --- | --- | --- |
| **T3** | Host exposes MCP tools but cannot run commands | Start setup, choose MCP | S1 records MCP `detected`; local commands `cannot determine`; no claim that `gh` is missing; no `ready` before a repository is bound | S1 output |
| **T4** | Host has no GitHub MCP tools, shell available | Start setup | MCP `unavailable` (inspector worked) or `unverified` (inspector unavailable); CLI path continues | S1 output plus which branch was taken |

## Group C — backend selection

| Case | Condition | Steps | Expected | Evidence to capture |
| --- | --- | --- | --- | --- |
| **T5** | Both backends configured, F-OK readable | Choose both, bind F-OK | Two independent rows at S7; each `ready` with its own evidence; no merged single verdict | S7 table |
| **T6** | `gh` installed, not logged in | Choose CLI | `unauthenticated`; instructs `gh auth login` in the operator's own terminal; never asks for a token | S4 output, absence of any token request |
| **T7** | `gh` not installed | Choose CLI | `unavailable`; points to the official install page; no unprompted install | S4 output |

## Group D — repository verdicts

| Case | Condition | Steps | Expected | Evidence to capture |
| --- | --- | --- | --- | --- |
| **T8** | MCP tool list inspected and genuinely empty | Start setup | `unavailable`, not `unverified` — the inspector worked | S1 output |
| **T9** | F-DENY prepared so the identity genuinely lacks access | Bind F-DENY | `insufficient-permissions` **only when an explicit `HTTP 403` is observed**, quoted verbatim. A private repository that is merely invisible to this identity can answer `404`; that outcome must be recorded `unverified`, never as `insufficient-permissions`. If a genuine `403` cannot be produced reliably, record the case `Not Run` | Status code plus raw message, or the Not Run reason |
| **T10** | F-GHOST (never created) | Bind F-GHOST | `unverified` plus the `404` ambiguity checklist; **must not** say `insufficient-permissions` | Verdict, checklist, absence of a permission claim |
| **T11** | Network path blocked or DNS blackholed | Bind F-OK while blocked | `unverified` with the reason; no invented state; no retry loop | Error text and stop behaviour |
| **T12** | F-NOMAIN (`master` only) | Bind F-NOMAIN | Reports missing `main` and asks how to proceed; creates no branch and substitutes no branch | Output, plus `git/ref` list showing no new branch |

## Group E — resilience

| Case | Condition | Steps | Expected | Evidence to capture |
| --- | --- | --- | --- | --- |
| **T13** | Interrupt during S2 or S5 | Stop the conversation, start a new session, re-run | Nothing persisted; re-probes from S1; no repeated installation guidance for a backend already present | Two transcripts, before and after |
| **T14** | Backend already `ready` | Ask to re-verify | Probes only; no installation or authentication guidance repeated | Output comparison with T5 |
| **T15** | One backend already configured | Ask to add the other | Only the new path runs, then S6 for it; the existing row is unchanged | S7 table before and after |
| **T16** | Two independently prepared conditions: MCP verified `ready` on F-OK, and the CLI identity restricted on that same repository | Choose both, bind F-OK | The two states are recorded separately, each from its own observation; the report states that the MCP backend is usable and the CLI one unresolved; no merged verdict and no global failure. If either half cannot be prepared, record `Not Run` instead of inferring the missing half | Both verdicts with their own evidence, or the Not Run reason |

## Group F — safety invariants

| Case | Condition | Steps | Expected | Evidence to capture |
| --- | --- | --- | --- | --- |
| **T17** | Any completed run | Count write operations in the whole transcript | Zero create/update/delete calls; target fixture commit count identical before and after; no branch, PR or issue created | Counts, `commits` count before/after, ref list |
| **T18** | Any completed run, in a local environment the operator controls | Compare authentication and configuration state before and after; publish only redacted results | Configuration and authentication state unchanged, and the Skill writes to no credential or environment file. The **public** record holds only redacted summaries, booleans, status names or digests — never tokens, authorization headers, raw environment values, sensitive file paths or other credential material, whether in the transcript, the case record or the S7 summary | Redacted comparison only: a file hash, `true`/`false`, or a status name, plus a grep result showing no credential pattern in the transcript |

## Run summary

Fill after the run; one line per case.

| Case | Status | Host | Target repo | Evidence |
| --- | --- | --- | --- | --- |
| T1 | Not Run | | | |
| … | Not Run | | | |
| T18 | Not Run | | | |

**Exit criterion:** the wizard may be described as acceptance-tested only when all 18 cases are
`Pass` on a recorded host. Until then, `README.md`, `docs/hermes.md` and this file must continue to
say the wizard has no end-to-end acceptance run.

## Limitations

- Manual, single host, single operator; language parity is judged by one bilingual operator.
- Negative cases are constructed (denied access, missing repository, blocked network), so they test
  the wizard's handling rather than GitHub's behaviour.
- No concurrency, load or multi-account scenario is covered; two independent human accounts are not
  exercised.
- Each `Pass` records one observation, not a guarantee for other hosts or other GitHub plans.
