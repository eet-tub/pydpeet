# Contributing to PyDPEET

Thank you for considering a contribution to PyDPEET.

PyDPEET focuses on reproducible battery data conversion, processing,
evaluation, and visualisation workflows. Small, well-scoped contributions are
the easiest to review and merge.

## Before you start

- For bugs, please open an issue with a minimal reproducible example when
  possible.
- For new features, please open or join an issue first so the maintainers can
  confirm the scope.
- For new data conversion support, include the cycler model, software version,
  export settings, battery type, and measurement description. If sample data is
  required, coordinate with the maintainers before sharing it.

## Development setup

The recommended local setup uses `uv` from the repository root:

```bash
uv sync --all-groups
```

The package is installed in editable mode, so local code changes are available
without reinstalling the package.

## Checks before submitting

Before opening a pull request, please run the relevant checks locally:

```bash
uv run pre-commit run --all-files
uv run pytest
```

If your change affects documentation, also build the documentation:

```bash
uv run python docs/build_docs.py
```

## Pull request expectations

- Keep the pull request focused on one topic.
- Add tests for new behavior or bug fixes.
- Update documentation when public behavior changes.
- Avoid committing generated artifacts unless the maintainers request them.
- Describe what changed and which checks you ran.

For more detail, see the developer guide in `docs/developer.md`.
