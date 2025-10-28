## ✅ Review Readiness Checklist (Required before review)

Complete all items below before marking your PR ready for review. After completion, delete these instructions and replace with your actual PR message.

- [ ] **PR title format**: `{TYPE}({SCOPE}): {DESCRIPTION}`
  - Examples:
    - `feat(cli): add cast scaffolding option`
    - `fix(scaffold): resolve snake_case normalization bug`
    - `docs(readme): clarify Python 3.12+ requirement`
  - Allowed `{TYPE}` values:
    - `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `release`
  - Allowed `{SCOPE}` values (optional): project area
    - `cli`, `scaffold`, `utils`, `docs`, `tests`, `workflow`, `cookiecutter`
  - Once you've written the title, delete this checklist item.

- [ ] **PR message**: Replace this entire checklist with the template below
  - **Description:** Describe the change. Include a [linking a pull request to an issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue) keyword if applicable.
  - **Issue:** The related issue number (e.g., `Fixes #123`)
  - **Dependencies:** Any dependencies required for this change
  - **SNS handle:** If announced publicly, add your handle for a shoutout

- [ ] **Add tests and docs**: If you add a new feature/integration, include
  1. **Tests:** Prefer unit tests without network access (integration tests as needed)
  2. **Docs/examples:** Update user-facing docs/examples
     - Update `README.md` or scaffold template docs (e.g., `act_operator/act_operator/scaffold/{{ cookiecutter.project_dir }}/README.md`)

- [ ] **Lint and test**: From the root of modified package(s), run and ensure all pass
  ```powershell
  uv run ruff check .
  uv run pytest -q
  ```
  We will not consider a PR unless these two pass in CI. See `CONTRIBUTING.md` for more.

### Additional guidelines
- Import optional dependencies **inside functions** (lazy import).
- Do not add dependencies to `pyproject.toml` (even optional) unless **required** for runtime/tests.
- Most PRs should modify **only one area/scope**.
- Changes must be **backwards compatible**.

---

## 📝 Summary

<!--
Provide a brief summary of the PR.
Example: Introduce cast addition option to the CLI and strengthen input validation.
-->

## 📄 Description

<!--
Describe the changes in detail.
Example: Enforce snake_case for scaffold directory names and auto-update related paths (pyproject.toml/langgraph.json).
-->

## 🔗 Issue / Dependencies / Mentions

- Issue: <!-- e.g., Fixes #123 -->
- Dependencies: <!-- e.g., ruff/pytest configuration changes -->
- SNS handle: <!-- add your handle if you want a public mention -->

## ✅ Local Checks

- [ ] `uv run ruff check .` passed
- [ ] `uv run pytest -q` passed

## 💡 Notes (Optional)

<!--
Add caveats/decisions/trade-offs/migration considerations for reviewers.
Example: This change updates template paths; existing projects are unaffected.
-->

## 🔗 Related Issue(s)

<!--
Mention related issues/PRs and specify any that should be closed.
Example: Related issues - #33, closes #27
-->
