# Plans

This folder is the standard location for checked-in task plans.

## Layout

- Put active or in-progress task plans under `docs/plans/active/`.
- Historical or superseded plan docs belong under `docs/archive/plans/`.
- Use the template at `docs/plans/active/TEMPLATE.md` for new work.

## When to use it

- Create or update a plan doc here for non-trivial work.
- A task is non-trivial if it touches multiple runtime layers, changes entrypoints/shared tooling, cleans up legacy material, or starts with architecture uncertainty.

## Naming

- Use `YYYY-MM-DD-short-slug.md` for plan instances.
- Keep the slug specific to the task, for example `2026-03-08-hud-loader-cleanup.md`.

## What a plan must contain

- Goal and scope
- Affected paths
- Validation to run
- Assumptions
- Open questions
- Expected doc updates

## Status and trust

- Plans are coordination artifacts, not architecture truth.
- Live code, scripts, configs, and test gates still win if a plan drifts from implementation.
- When a plan is superseded, mark it clearly instead of silently leaving it to look current.
