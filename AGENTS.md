# Visual Task Factory Engineering Rules

This repository implements Track 2 of the Visual Task Factory. Correctness,
reproducibility, and validity take priority over feature count.

## Non-negotiable rules

1. **Ground truth:** Reference answers come only from the scene spec through pure
   functions in `answers.py`. No model/API client may be imported in scene,
   render, or questions modules. Maintain a test enforcing this boundary.
2. **Determinism:** Seed every stochastic operation; the same spec must produce
   the same image hash. Pin versions in `requirements.txt` and use Matplotlib's
   `Agg` backend.
3. **Single source of truth:** The spec decides all scene content. The renderer
   only draws it and never makes decisions.
4. **Differentiator fields from day one:** Schemas must include `distractors`,
   `pair_id`, `variant_of`, `factor_changed`, and `severity_params`.
5. **Tests first:** Every function gets a unit test. Answer and misconception
   functions must be tested against hand-computed values, shown in test comments.
6. **No fake results:** Never present mocked data as real, hardcode outputs,
   silently catch exceptions, or loosen a test merely to make it pass.
7. **Check uncertain APIs:** Do not invent library APIs. Verify installed-version
   documentation or run a small experiment for uncertain Matplotlib, OpenCV, or
   model-SDK behavior.
8. **Tight scope:** Do only the current phase. Do not refactor earlier phases
   unless a test proves a bug.
9. **Budget safety:** Every model API call goes through the cache and a hard
   spend cap. Never run a large evaluation without user approval.
10. **Secrets:** Read API keys only from environment variables; never put them
    in code, logs, or commits.

## Required phase loop

For every phase:

1. **Plan:** Restate the goal, files to create/change, and documented acceptance
   criteria.
2. **Tests first:** Write unit, edge-case, and phase-specific golden-fixture tests.
3. **Implement:** Write minimal, typed, documented public APIs.
4. **Run:** Run the full test suite; fix code rather than weakening tests.
5. **Verify:** Perform the phase-specific evidence checks, including determinism
   and sample generation where applicable.
6. **Report:** State what was built, exact test command and counts, verification
   evidence, limitations/risks, and judgment calls requiring review.
7. **Commit:** Make a clear commit and stop for user approval before the next
   phase.

If the same test failure occurs three times, stop and explain the root cause.
If the documents reveal a design flaw, stop and propose a fix rather than
silently deviating.

## Phase order

1. Repo skeleton, pinned requirements, Typer CLI skeleton, Pydantic schemas,
   config, tests, and mock model adapter.
2. Scene generator and renderer for bar, line, and scatter; effects, pixel boxes,
   and one-factor scene pairs.
3. Six-skill question templates, pure answers, misconception distractors, and
   collision handling.
4. Re-extraction, ambiguity, evidence, image-necessity, duplicate validators,
   and golden bad fixtures.
5. Full generation, balancing, evaluation adapters/runner/cache/budget/scorer,
   and severity scoring.
6. Accuracy confidence intervals, degradation curves, classifier, pair analysis,
   severity sensitivity, and audit export.
7. Static report, `vtf demo` with cached fallback, README, and clean-clone check.

Do not begin a later phase until the user explicitly approves it.
