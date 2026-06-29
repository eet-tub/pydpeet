# Developer Guide

This page describes the recommended workflow for contributors who implement new functions, extend the public API, or rebuild the documentation.

## Development environment

The recommended setup is a dedicated `uv` environment with an editable install of the package.

Make sure `uv` is installed first. Installation instructions are available in the official uv documentation:

```text
https://docs.astral.sh/uv/getting-started/installation/
```

Create the development environment from the repository root:

```bash
uv sync --all-groups
```

This creates a local `.venv` environment and installs the project together with the configured development, documentation, test, and linting dependencies.

If you need to use a specific Python version, pin it first:

```bash
uv python pin 3.12
uv sync --all-groups
```

The package is installed in editable mode by `uv`, so local code changes are immediately available without reinstalling the package.

## Use pre-commit before committing

This repository uses `pre-commit` to run the configured linters and formatters automatically.

Install it once in your local clone:

```bash
uv run pre-commit install
```

Run it on all files at any time:

```bash
uv run pre-commit run --all-files
```

The current pre-commit configuration runs Ruff checks and Ruff formatting. Contributors should run these checks locally before pushing code so that style issues are resolved early instead of in code review.

## Build the documentation

The documentation is built with Sphinx, MyST Markdown, nbsphinx, and sphinx-design.

Before rebuilding the documentation locally, make sure that:

- the uv environment is synchronized
- the documentation dependencies are installed
- `pandoc` is installed and available on `PATH`

Install `pandoc` separately if it is not already available.

Build the HTML documentation with:

```bash
uv run sphinx-build -b html docs docs/_build/html
```

This command builds the documentation from the existing source files and writes the HTML output to `docs/_build/html`.

If the API reference pages need to be regenerated, run the documentation build script instead:

```bash
uv run python docs/build_docs.py
```

This script performs two steps:

1. It regenerates API stubs from the Python package.
2. It builds the HTML documentation.

If the build fails after `pandoc` is available, the next likely cause is invalid docstring formatting in public functions. In that case, fix the affected docstrings first, because Sphinx parses them while generating the API pages.

The repository CI follows the same idea:

* GitLab CI installs `pandoc`, runs `uv sync --all-groups`, and then runs `uv run python docs/build_docs.py`
* GitHub Pages installs `pandoc`, runs `uv sync --all-groups`, and then runs `uv run python docs/build_docs.py`




## Add new public functions correctly

When you implement a new function, make sure it is added to the correct public `__init__.py` file if it should become part of the documented public API.

This matters for three reasons:

- Users should only rely on stable, intentionally exported functions.
- The generated API reference should stay limited to the real public surface.
- New public functions can only be documented automatically if they are reachable through the package API.

A good rule is:

- Keep internal helpers internal.
- Export only the functions that should be imported by users.
- Add a proper docstring before exposing a function publicly.

## Write documentation for every public function

Each public function should be documented in a style that works well with generated API pages, similar to NumPy-style documentation.

Every public function page should have at least:

- a short summary
- clear parameter descriptions
- the return value
- an `Examples` section
- ideally a `See also` section that points to related functionality

## Tests are required

Every new function must come with tests.

At minimum, tests should cover:

- the expected main behaviour
- important edge cases
- failure modes or invalid input handling
- regressions for bugs that were fixed during development

Run the test suite before opening a merge request:

```bash
uv run pytest
```

## Recommended contribution checklist

Before you submit code, verify the following:

- the environment was synchronized with `uv sync --all-groups`
- the function is implemented and intentionally placed in the package structure
- the relevant `__init__.py` exports are updated if the function is public
- the docstring is complete enough for the generated API page
- tests were added and pass
- `uv run pre-commit run --all-files` passes
- the documentation was rebuilt successfully if user-facing behaviour changed
