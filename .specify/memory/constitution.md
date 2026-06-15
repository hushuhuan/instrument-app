<!--
Sync Impact Report
- Version change: 1.3.0 → 1.4.0
- Modified principles: N/A (renumber N/A); added **IX. Python Implementation Stack**
- Added sections: Principle IX; Governance / compliance bullet for IX
- Removed sections: N/A
- Renamed document title: "CPP Constitution" → "Project Constitution" (stack Mandate is Python; repo path may remain legacy)
- Templates: .specify/templates/plan-template.md ✅ | .specify/templates/spec-template.md ✅ | .specify/templates/tasks-template.md ✅ | `specs/001-organic-synthesis-control/plan.md` ✅ (tech stack aligned)
- Follow-up TODOs: Regenerate or amend `tasks.md` / retire C++ tree under repo root if migrating codebase to Python layout
-->

# Project Constitution

## Core Principles

### I. Think Before Coding — Assumptions & Uncertainty

Before implementation, every contributor and automation (including AI agents) MUST state
material assumptions explicitly. When information is uncertain, missing, or based on a
guess, they MUST surface that uncertainty and ask for confirmation rather than acting
as if the guess were fact. Rationale: silent assumptions compound errors and make
reviews ineffective.

### II. Think Before Coding — Disambiguation & Tradeoffs

When multiple reasonable interpretations of requirements, interfaces, or behavior
exist, they MUST be listed with their tradeoffs. Choosing one interpretation without
surfacing the alternatives is forbidden for decisions that affect scope, safety, APIs,
or user-visible behavior. Rationale: the cheapest fix is resolving ambiguity before code
exists.

### III. Think Before Coding — Simplicity & Pushback

Before locking in a design, contributors MUST note a simpler approach when one exists.
If a more complex path is taken, the plan or recorded discussion MUST justify why the
simpler option was rejected or insufficient. Contributors MUST push back—clearly and
constructively—when directions are unclear, over-scoped, or risky rather than
proceeding to please a prompt. Rationale: complexity must be earned, not accidental.

### IV. Think Before Coding — Stop on Confusion

If requirements, constraints, acceptance criteria, or dependencies are unclear,
implementation-oriented work MUST pause. The confusion MUST be named concretely, and
clarification MUST be obtained (e.g. spec update, `/speckit-clarify`, or human review)
before coding continues. Rationale: coding through confusion ships the wrong product
faster.

### V. Specification Traceability

Work products MUST remain traceable to the governing Spec Kit artifacts for the
feature (`spec.md`, `plan.md`, `tasks.md` under the feature spec directory). Deviations
from those artifacts MUST be explicit: documented in the spec/plan/tasks with rationale,
not buried only in code or chat. Rationale: governance applies to the record the team
relies on, not to unwritten intent.

### VI. Simplicity First

Implementation MUST be the minimum code and structure that correctly satisfies the
stated problem and acceptance criteria. Features, behaviors, or options beyond what the
spec or plan explicitly calls for MUST NOT be added. Abstractions (classes, layers,
helpers, plugins) MUST NOT be introduced when they exist only for a single use unless
the spec requires extensibility. Flexibility, configurability, feature flags, optional
code paths, or "future-proof" hooks MUST NOT be added unless that need is recorded in
the governing artifacts. Error handling and branches for scenarios treated as
impossible or out of scope in the spec MUST NOT be written to satisfy hypothetical
cases. Before completing work, if a correct solution could be materially smaller,
contributors MUST refactor or rewrite toward that smaller solution. As a final check:
if a senior engineer would fairly judge the result overcomplicated for the scoped
problem, it MUST be simplified. Rationale: speculative code increases defects,
review load, and maintenance cost without stakeholder value—Principle VI applies at
implementation time; Principle III governs design-time simplicity and pushback.

### VII. Surgical Changes

When modifying existing code, contributors MUST change only what is required to satisfy
the active request or the governing spec, plan, or task. They MUST NOT refactor,
reformat, restyle, or "improve" adjacent code, comments, or formatting unless that work
is explicitly requested or strictly required for correctness or safety of the change.
They MUST match the file's and project's established style even when they would choose
differently. If they notice unrelated dead code or pre-existing issues, they MAY note
them for follow-up but MUST NOT delete or repair them unless asked. When their edits
render imports, variables, or functions unused, they MUST remove only those orphans
that their change created; pre-existing dead code MUST NOT be removed unless
explicitly requested. Review criterion: every modified line MUST trace directly to
the user request or governing artifact—otherwise it MUST be reverted or split into a
separate change. Rationale: scope creep in diffs obscures intent, increases review cost,
and raises merge and regression risk without stakeholder approval.

### VIII. Goal-Driven Execution

Work MUST start from explicit, verifiable success criteria—not from vague intent such as
"make it work." Before implementation, contributors MUST reframe underspecified tasks as
goals with a concrete verification method: for example, "add validation" becomes tests
(or equivalent checks) for invalid inputs that fail before the change and pass after;
"fix the bug" becomes a reproduction test or agreed repro procedure that fails before
the fix and passes after; "refactor X" requires the project's agreed automated checks
(typically the full relevant test suite) to pass before and after, or another verification
named in the spec or plan if tests are not applicable. Multi-step work MUST include a
short numbered plan where each step lists what will be verified before moving on
(e.g. `1. [Step] → verify: [check]`). Execution MUST loop—implement, run verification,
fix—until those criteria pass; declaring completion with failing or unrunnable checks is
forbidden. Rationale: strong, checkable criteria let contributors and reviewers iterate
independently; weak criteria recreate constant clarification and hidden rework.

### IX. Python Implementation Stack

Application implementation for this product (GUI, domain logic, orchestration, HAL
abstractions, persistence glue, and automated tests) MUST be written in **Python**,
unless an amendment to this constitution explicitly authorizes another language for a
named, bounded component—and that exception MUST be recorded in `plan.md` with
rationale and scope. Native extensions or vendor SDKs MAY ship as separate binaries
**only** when required for hardware or performance, and MUST be thinly wrapped behind
Python interfaces traceable in the plan. Rationale: a single primary language reduces
toolchain sprawl, aligns CI and packaging, and keeps Spec Kit tasks executable by one
stack; the prior C++ direction is superseded for new feature work by governance choice,
not by ad hoc preference.

## Agent & Contributor Conduct

- **No performative certainty**: Do not imply confidence when the basis is incomplete;
  prefer `NEEDS CLARIFICATION`, explicit options, or questions.
- **Surface tradeoffs, not just picks**: When recommending an approach, briefly state
  what is given up relative to reasonable alternatives.
- **Supplementary guidance**: `.cursor/rules/` and other project rules align with
  this constitution; where they conflict, this file takes precedence for governance
  and gates, and dependent templates MUST be updated when this constitution changes.

## Spec Kit Workflow

- **Specify before build**: Functional intent and acceptance criteria live in the spec;
  plans interpret spec, tasks decompose plan—skipping or collapsing these steps without
  cause violates traceability (Principle V).
- **Clarify early**: Use clarification workflows when ambiguity blocks a clean plan or
  task list; do not "code around" missing decisions.
- **Check at plan time**: `plan.md` MUST satisfy the Constitution Check gates defined
  in `.specify/templates/plan-template.md` before Phase 0 research proceeds, and MUST
  be revalidated after Phase 1 design. Plans MUST state the Python runtime, packaging,
  and primary GUI/framework libraries (per Principle IX).
- **Tasks and verification**: `tasks.md` entries MUST be framed so each task has
  verifiable completion per Principle VIII (observable checks, not vague "done"), and MUST
  reference Python modules or scripts where implementation applies (Principle IX).

## Governance

- **Supremacy**: This constitution supersedes ad hoc process for Spec Kit–driven work
  in this repository. Feature work MUST comply through spec, plan, and task artifacts.
- **Amendments**: Amendments are made by editing `.specify/memory/constitution.md`,
  bumping **Version** per semantic versioning below, updating **Last Amended**, and
  propagating changes to dependent templates and guidance until the Sync Impact Report
  shows no pending template work.
- **Versioning policy**:
  - **MAJOR**: Removal or incompatible redefinition of a principle, or governance
    that breaks existing compliance expectations.
  - **MINOR**: New principle or section, or materially expanded guidance.
  - **PATCH**: Wording, clarity, typos, or non-semantic refinements.
- **Compliance review**: Authors and reviewers MUST confirm that plans and significant
  PRs respect Principles I–IX. **Implementation language** (Principle IX): new code in
  scope MUST be Python unless a documented exception appears in the plan amendment
  process. Design complexity that cuts against simplicity (Principle III) MUST appear
  in the plan's Complexity Tracking table where that template provides it. Reviews MUST
  verify scope-bound implementation (Principle VI): no unrequested features,
  abstractions, or configurability; no defensive code for impossible scenarios per spec.
  Reviews MUST verify surgical diffs (Principle VII): no drive-by refactors or cleanup
  unless requested; every changed line traceable to the task or request. Reviews MUST
  verify goal-driven completion (Principle VIII): stated verification for the change
  passes; vague "done" without a check is insufficient.

**Version**: 1.4.0 | **Ratified**: 2026-05-05 | **Last Amended**: 2026-05-05
