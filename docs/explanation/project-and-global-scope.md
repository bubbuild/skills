# Project And Global Scope

Project scope is the default.

A project is discovered from `skills.toml` or `pyproject.toml`. Project state is
stored under that project root:

```text
.skills/
  installed/
  skills.lock
.agents/
  skills/
```

Two projects can install the same skill name without sharing state.

Global scope is explicit. Use `--global` in the CLI or `global_install=True` in
the library when the skill should be shared across projects.

Global state uses:

- `state_dir` for canonical installed state and lock file;
- `~/.agents/skills` for the built-in global target.
