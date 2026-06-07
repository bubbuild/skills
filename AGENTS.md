# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python package using a `src` layout. Core library code lives in `src/skills/`. Important subpackages include `cli/` for command adapters, `features/` for manager workflows, `builtin/` for built-in source and target plugins, and top-level modules such as `manager.py`, `project.py`, `config.py`, and `plugins.py` for orchestration and public APIs. Tests live in `tests/`. Documentation is under `docs/`, and bundled agent skills live in `skills/`.

## Build, Test, and Development Commands

- `uv sync`: install the project and development dependencies.
- `uv run skills --help`: run the CLI locally.
- `make test`: run the pytest suite with doctest modules.
- `make check`: verify the lock file, run pre-commit hooks, and run mypy.
- `uv run ruff check .`: run lint checks directly.
- `uv run mypy`: run static type checks.
- `make docs-test`: build documentation strictly with MkDocs.
- `make build`: build distribution artifacts in `dist/`.

## Coding Style & Naming Conventions

Use Python 3.10+ syntax and keep code typed. Public functions and methods should have clear, stable return types. Prefer `pathlib.Path` for filesystem work, small functions, and explicit error classes for user-facing failures. Ruff enforces linting and import order with a 120-character line length. Test files use `test_*.py`; CLI command modules use short command names such as `add.py`, `use.py`, and `remove.py`.

## Testing Guidelines

Use pytest. Add focused tests beside related behavior in `tests/`, especially for CLI routing, manager lifecycle, config scope, hooks, and lock handling. Use `tmp_path` for filesystem tests and avoid touching user-level state unless the test explicitly covers global behavior. Run `make test` or `uv run pytest tests` before submitting changes.

## Commit & Pull Request Guidelines

Recent history uses Conventional Commit-style subjects, for example `feat: add prompt rendering hook`, `fix: harden skills config and lock handling`, and `refactor: constrain skills config sources`. Keep commits scoped and descriptive. Pull requests should explain the behavior change, include tests for code changes, update docs for public APIs or CLI behavior, and mention any compatibility impact.

## Agent-Specific Instructions

Keep feature modules above hooks in the dependency direction: features may call plugin hooks, but plugins should not redefine feature control flow. Built-in behavior should stay small and predictable; add extension points only when they preserve default behavior.
