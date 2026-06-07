# skills

`skills` manages agent skills for a project or an application.

It provides:

- a Python library API for applications that want built-in skills management;
- a CLI for the same workflows;
- project-scoped installs by default;
- optional global installs with `--global`;
- built-in local/Git sources and the `.agents/skills` target;
- Pluggy hooks for adding sources, targets, and extra config sources.

## Library First

Use `SkillsManager` when embedding skills support:

```python
from skills import SkillsManager

manager = SkillsManager("/path/to/project")
manager.add("./my-skills", skills=["code-review"], mode="copy")

prompt = manager.use("code-review").prompt
installed = manager.installed()
```

The CLI uses the same manager internally:

```text
cli -> SkillsManager -> feature modules -> hooks/plugins
```

## CLI Basics

```bash
skills init code-review --description "Review code changes."
skills add ./my-skills --skill code-review --copy
skills use code-review
skills installed
skills update code-review
skills remove code-review
```

## Project Configuration

Use `skills.toml` for any project:

```toml
agents = ["agents"]

[install]
mode = "symlink"
```

`skills.toml` is the built-in project config file. Python-specific
`pyproject.toml` sections such as `[tool.skills]` are not read by default.
Plugins may provide extra read-only config sources, but `skills.toml` remains
the project-local override.

## State Model

Project installs are isolated by project root:

```text
.skills/
  installed/<skill-name>/
  skills.lock
.agents/
  skills/<skill-name>/
```

Use `--global` only when you want shared global state.

## Documentation

- Start with `docs/tutorials/getting-started.md`.
- Use `docs/how-to/use-as-library.md` when embedding `skills`.
- Use `docs/reference/cli.md` and `docs/reference/configuration.md` for exact options.
- Use `docs/explanation/design.md` for the design model.

## Bundled Skills

The repository includes `skills/skills-manager`, a skill for agents working on
this package or embedding it elsewhere. Tests also install from the repository
`skills/` directory to exercise the real source layout.

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```
