name: "✨ Feature Request (EN)"
description: Propose a new feature or improvement for Act Operator CLI.
labels: [pending, enhancement]
body:
  - type: markdown
    attributes:
      value: |
        Thank you for contributing ideas to improve Act Operator!

        Use this form to propose a feature or enhancement for Act Operator (CLI for bootstrapping LangGraph-based “Act - AX Template” blueprints).
        For general questions or discussion, please use our Discord.

        Before filing, please check the following resources to see if a similar request already exists:

        * Act Operator README: https://github.com/Proact0/Act-Operator#readme
        * Act Operator GitHub Issues: https://github.com/Proact0/Act-Operator/issues
        * GitHub search in this repo: https://github.com/Proact0/Act-Operator
        * Our Discord: https://discord.gg/4GTNbEy5EB
  - type: checkboxes
    id: checks
    attributes:
      label: Checked other resources
      description: Before submitting, please confirm the following.
      options:
        - label: This is a feature request/enhancement for Act Operator CLI, not a bug report.
          required: true
        - label: I added a clear, concise, and descriptive title for the proposal.
          required: true
        - label: I searched existing issues/PRs and did not find a duplicate.
          required: true
  - type: textarea
    id: description
    validations:
      required: true
    attributes:
      label: Summary
      description: |
        What feature or improvement would you like to see?
        Explain the motivation, goals, and how it benefits users.
      placeholder: |
        * I propose adding X to support Y.
        * It would help users by Z.
  - type: textarea
    id: use-case
    validations:
      required: true
    attributes:
      label: Use Case / Scenarios
      description: Describe typical workflows or scenarios where this feature is useful.
      placeholder: |
        * When scaffolding ..., I need ...
        * When adding casts ..., it would be helpful to ...
  - type: textarea
    id: proposal
    validations:
      required: false
    attributes:
      label: Proposed Solution / UX
      description: |
        Provide ideas for CLI flags, prompts, configuration, or example commands.
      placeholder: |
        Example CLI:
        uv run act new --path ./my-act --act-name "My Act" --cast-name "Main Cast" --flag ...
  - type: textarea
    id: alternatives
    validations:
      required: false
    attributes:
      label: Alternatives Considered
      description: If applicable, describe alternative approaches and trade-offs.
  - type: textarea
    id: references
    validations:
      required: false
    attributes:
      label: References (optional)
      description: Links to related issues, PRs, or docs.
  - type: textarea
    id: screenshots
    validations:
      required: false
    attributes:
      label: Mockups / Examples (optional)
      description: If applicable, add screenshots or pseudo-output to illustrate the proposal.
  - type: textarea
    id: additional
    validations:
      required: false
    attributes:
      label: Additional context
      description: Any other context or considerations.
  - type: markdown
    attributes:
      value: |
        Branching tip: create a branch named `feat/[concise-feature-name]` when you start working on this.
        Remember to keep PRs small and focused.
