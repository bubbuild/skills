# Getting Started

This tutorial installs a local skill into a project and renders it.

## Create A Skill

```bash
skills init code-review --description "Review code changes."
```

This creates:

```text
code-review/
  SKILL.md
```

## Configure The Project

Create `skills.toml`:

```toml
agents = ["agents"]

[install]
mode = "symlink"
```

## Install The Skill

```bash
skills add . --skill code-review
```

The project now has managed state:

```text
.skills/
  installed/code-review/
  skills.lock
.agents/
  skills/code-review/
```

## Render The Skill

```bash
skills use code-review
```

The command prints the installed `SKILL.md`.

## Update And Remove

After changing `code-review/SKILL.md`, update the installed copy:

```bash
skills update code-review
```

Remove it:

```bash
skills remove code-review
```
