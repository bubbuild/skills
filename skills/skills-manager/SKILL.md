---
name: skills-manager
description: Use when an agent needs to use, test, or extend the bubbuild/skills library or CLI. Covers the public SkillsManager API, CLI workflows, project/global scope behavior, configuration, plugin boundaries, and repository tests for this package.
---

# Skills Manager

Use this skill when working inside the `bubbuild/skills` project or when adding
skills management support to another agent/application.

## Entry Points

Prefer the library API for embedded behavior:

```python
from skills import SkillsManager

manager = SkillsManager("/path/to/project")
manager.add("./my-skills", skills=["code-review"], mode="copy")
prompt = manager.use("code-review").prompt
```

Use the CLI for shell workflows:

```bash
skills add ./my-skills --skill code-review --copy
skills use code-review
skills installed
skills update code-review
skills remove code-review
```

Do not call internal feature modules from application code. The intended chain
is:

```text
cli -> SkillsManager -> features -> hooks/plugins
```

## Scope Rules

Project scope is the default. Project state lives under the discovered project
root:

```text
.skills/skills.lock
.skills/installed/<skill>/
.agents/skills/<skill>/
```

Use `global_install=True` or `--global` only for shared global state.

## Configuration

Use `skills.toml` for skills-native configuration:

```toml
agents = ["agents"]

[install]
mode = "symlink"
```

`skills.toml` is the built-in project config file. Python-specific
`pyproject.toml` sections are not read by default. Plugins may provide extra
config sources, but they are lower priority than `skills.toml`.

Supported keys:

- `agents`: default install targets.
- `install.mode`: `symlink` or `copy`.
- `cache_dir`: global-only source cache directory.
- `state_dir`: global-only install state directory.

## Plugin Boundary

Core built-ins are intentionally small:

- local/Git sources;
- `.agents/skills` target;
- `skills.toml` project config and lower-priority plugin config sources.

Add other agents or source formats through Pluggy hooks. Export plugin classes
through the `skills` entry point group and use `from skills import hookimpl`.

## Tests

Use the repository's `skills/` directory as the real skill source in tests when
testing packaged skills:

```python
source = repo_root / "skills"
manager.add(str(source), skills=["skills-manager"], mode="copy")
```

Run validation before finishing changes:

```bash
uv run pytest
uv run ruff check .
uv run mypy
uv run mkdocs build --strict
```
