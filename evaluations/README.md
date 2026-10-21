# Evaluating InfraKeeper

Use `cases.json` as a qualitative regression suite. Give an evaluator the skill, one case request, and only the specified repository fixture. Score each `must_do` as met or unmet and fail the case if any `must_not_do` behavior appears.

The scenarios target reasoning behavior: evidence boundaries, relevant record discovery, authorization, conflict analysis, validation, rollback, and secret handling. They intentionally do not prescribe an exact response format.
