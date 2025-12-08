name: "🐛 Bug Report (EN)"
description: Report a bug in Act Operator CLI. For security issues, please use GitHub Security Advisories (Security tab). For usage questions, please use our Discord.
labels: [pending, bug]
body:
  - type: markdown
    attributes:
      value: |
        Thank you for taking the time to file a bug report.

        Use this to report BUGS in Act Operator (CLI for bootstrapping LangGraph-based “Act - AX Template” blueprints).
        For usage questions, feature requests and general design questions, please use our Discord.

        Before filing, please check the following resources to see if your issue has already been reported or solved:

        * Act Operator README: https://github.com/Proact0/Act-Operator#readme
        * Act Operator GitHub Issues: https://github.com/Proact0/Act-Operator/issues
        * GitHub search in this repo: https://github.com/Proact0/Act-Operator
        * uv documentation: https://docs.astral.sh/uv/
        * Our Discord: https://discord.gg/4GTNbEy5EB
  - type: checkboxes
    id: checks
    attributes:
      label: Checked other resources
      description: Before submitting, please confirm the following.
      options:
        - label: This is a bug in Act Operator CLI, not a usage question. For questions, please use Proact0 Discord Community(https://discord.gg/4GTNbEy5EB).
          required: true
        - label: I added a clear, concise, and detailed title summarizing the issue.
          required: true
        - label: I read what a minimal reproducible example is (https://stackoverflow.com/help/minimal-reproducible-example).
          required: true
        - label: I included self-contained minimal reproduction steps, including the exact CLI commands or code used.
          required: true
  - type: textarea
    id: reproduction
    validations:
      required: true
    attributes:
      label: Reproduction Steps and Example Commands
      description: |
        Please add a self-contained minimal reproduction with exact steps and commands.
        Replace the example below with your own!
      placeholder: |
        # Steps
        1. Run the following commands

        # Example commands
        uv run act new --act-name "Demo Act" --cast-name "Main Cast"
        uv run act cast --path ./demo-act --cast-name "Support Cast"

        # Observed behavior
        - Describe what happens

        # Expected behavior
        - Describe what you expected instead
      render: shell
  - type: textarea
    id: error
    validations:
      required: false
    attributes:
      label: Error Message and Stack Trace (if applicable)
      description: |
        If you are reporting an error, please include the full error message and stack trace.
      placeholder: |
        Exception + full stack trace
      render: shell
  - type: textarea
    id: description
    validations:
      required: true
    attributes:
      label: Description
      description: |
        What is the problem?
        Write a short description telling what you are doing, what you expect to happen, and what is currently happening.
      placeholder: |
        * I'm trying to use the Act Operator CLI to scaffold X.
        * I expect to see Y.
        * Instead, it does Z.
  - type: textarea
    id: screenshots
    validations:
      required: false
    attributes:
      label: Screenshots (optional)
      description: If applicable, add screenshots to help explain the problem.
  - type: textarea
    id: system-info
    attributes:
      label: System Info
      description: |
        Please provide the following details. Paste command outputs where relevant.
      placeholder: |
        OS: Windows/macOS/Linux + version
        Python: output of `python --version`
        uv: output of `uv --version`
        Act Operator version: output of `python -c "import act_operator; print(getattr(act_operator, '__version__', 'unknown'))"`
        Installation method: uv/pip/pipx/other
        Virtual environment: yes/no (and which tool)
    validations:
      required: true