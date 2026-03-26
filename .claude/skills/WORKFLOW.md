```
+----------------------------------------------------------------------+
|                HOW TO USE — PRACTICAL GUIDE                           |
+----------------------------------------------------------------------+
|                                                                      |
|  Skills are slash commands you type in Claude Code.                   |
|  They automate checks so you don't forget steps.                     |
|                                                                      |
|  SCENARIO 1: Starting a new task                                     |
|                                                                      |
|    /resume                                                           |
|    -> Claude reads your plan, git log, issues                        |
|    -> Tells you: "Next: Phase 2 — add recurrence logic"              |
|                                                                      |
|    ... write code ...                                                |
|                                                                      |
|    /redo tests                                                       |
|    -> Runs: pytest --tb=short -q                                     |
|    -> Shows: 14 passed, 0 failed                                     |
|                                                                      |
|    /review nai_planner/contrib/drf/views.py                          |
|    -> Claude reads the file, checks for bugs                         |
|    -> Reports: "2 issues: missing select_related, N+1 query"         |
|                                                                      |
|    ... fix the issues ...                                            |
|                                                                      |
|    /pre-commit                                                       |
|    -> Scans staged changes for secrets, security issues, etc         |
|    -> APPROVED -> safe to push                                       |
|    -> BLOCKED -> tells you exactly what to fix                       |
|                                                                      |
|  SCENARIO 2: Ready to publish a new version to PyPI                  |
|                                                                      |
|    /test-suite                                                       |
|    -> Finds untested code in nai_planner/                            |
|    -> Generates test files in tests/                                 |
|    -> Runs pytest — all must pass                                    |
|                                                                      |
|    /release-check                                                    |
|    -> Checks: version bumped? tests pass? package builds?            |
|    -> READY -> publish with: python -m build && twine upload         |
|    -> NOT READY -> fix blockers first                                |
|                                                                      |
|  SCENARIO 3: Something feels slow or wrong                           |
|                                                                      |
|    /perf-audit                                                       |
|    -> Checks N+1 queries, index coverage, task performance           |
|                                                                      |
|    /full-app-audit                                                   |
|    -> Nuclear option — checks EVERYTHING                             |
|    -> Models, API views, tasks, code quality, deps                   |
|    -> Writes all findings to docs/issues.md                          |
|                                                                      |
|    /dep-audit                                                        |
|    -> Checks pyproject.toml for outdated/unused/vulnerable           |
|                                                                      |
|    /api-audit                                                        |
|    -> Checks public exports, serializers, schemas, admin             |
|                                                                      |
|  SCENARIO 4: Finished a plan, need final verification                |
|                                                                      |
|    /validate                                                         |
|    -> Reads your plan file                                           |
|    -> Checks every [x] task actually exists in code                  |
|    -> Runs pytest + ruff                                             |
|    -> Checks models, API surface, migrations                         |
|    -> VALIDATED -> safe to commit                                    |
|                                                                      |
|  TYPICAL DAILY FLOW                                                  |
|                                                                      |
|    /resume              <- where was I?                              |
|    ... write code ...                                                |
|    /redo tests          <- did I break anything?                     |
|    /review <file>       <- is this file clean?                       |
|    /validate            <- is the plan done correctly?               |
|    /pre-commit          <- safe to push?                             |
|    git push                                                          |
|                                                                      |
|    RELEASE DAY (add these before publish):                           |
|    /test-suite          <- generate + run all tests                  |
|    /release-check       <- ready for PyPI?                           |
|    python -m build && twine upload dist/*                            |
|                                                                      |
+----------------------------------------------------------------------+
|                                                                      |
|   NONE of these skills modify your code (except /test-suite).        |
|   They REPORT only. You decide what to fix.                          |
|                                                                      |
+----------------------------------------------------------------------+


+----------------------------------------------------------------------+
|              SKILL USAGE WORKFLOW — NAI-PLANNER                       |
+----------------------------------------------------------------------+
|                                                                      |
|   PRIORITY GUIDE                                                     |
|   P0 = every push       (mandatory)                                  |
|   P1 = every session     (recommended)                               |
|   P2 = as needed         (during dev)                                |
|   P3 = per release       (milestone gate)                            |
|   P4 = monthly/quarterly (health check)                              |
|                                                                      |
|   START SESSION                                                      |
|   |                                                                  |
|   v                                                                  |
|   /resume ------- P1 - every session start                           |
|   |  Rebuilds context from plan, git, issues                         |
|   |                                                                  |
|   v                                                                  |
|   Write Plan ---- docs/plans/YYYY-MM-DD-task.md                      |
|   |                                                                  |
|   v                                                                  |
|   IMPLEMENT (code, test, run)                                        |
|   |                                                                  |
|   v                                                                  |
|   /redo ------- P1 - after every fix                                 |
|   |  Re-runs ruff, pytest                                            |
|   |                                                                  |
|   v                                                                  |
|   QUALITY GATES (use by need)                                        |
|                                                                      |
|     /review ------ P2 - when you want a second eye                   |
|     /validate ---- P2 - when plan is done                            |
|     /perf-audit -- P4 - per major feature                            |
|     /api-audit --- P4 - after changing public API                    |
|   |                                                                  |
|   v                                                                  |
|   /pre-commit ------ P0 - EVERY push (mandatory)                    |
|   |  Secrets, security, code standards                               |
|   |                                                                  |
|   +-- APPROVED -> git push                                           |
|   +-- BLOCKED -> fix -> /redo -> /pre-commit again                   |
|   |                                                                  |
|   v                                                                  |
|   RELEASE PIPELINE (PyPI publish)                                    |
|                                                                      |
|     /dep-audit ------ P4 - monthly or before release                 |
|     /full-app-audit -- P3 - quarterly or major release               |
|     /test-suite ----- P3 - before every release                      |
|     /release-check -- P3 - before PyPI publish                       |
|   |                                                                  |
|   v                                                                  |
|   PUBLISH TO PYPI                                                    |
|                                                                      |
+----------------------------------------------------------------------+
|                                                                      |
|   ALL SKILLS (12)                                                    |
|   /resume        P1  rebuild context, find next action               |
|   /redo          P1  re-run tests, lint, check                       |
|   /review        P2  quick targeted file review                      |
|   /validate      P2  verify plan vs implementation                   |
|   /pre-commit    P0  MANDATORY gate before git push                  |
|   /perf-audit    P4  query & task performance scan                   |
|   /api-audit     P4  library public API validation                   |
|   /dep-audit     P4  pyproject.toml health check                     |
|   /full-app-audit P3 deep audit of entire package                    |
|   /test-suite    P3  generate tests + verify all green               |
|   /release-check P3  PyPI publish readiness                          |
|   /push-changelog -- push changelog to nemati.ai API                 |
|                                                                      |
|   ALL COMMANDS RUN LOCALLY: pytest, ruff, python -m build            |
|                                                                      |
+----------------------------------------------------------------------+
```
