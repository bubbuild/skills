# skills

`skills` manages agent skills through a Python library API and a CLI.

Use it when you want a project or application to install, update, render, and
remove skills without hard-coding every agent integration into the core package.

## Start Here

- New to the project: [Getting started](tutorials/getting-started.md)
- Embedding skills in an application: [Use skills as a library](how-to/use-as-library.md)
- Installing from the CLI: [Use the CLI](how-to/use-the-cli.md)
- Understanding project and global state: [Project and global scope](explanation/project-and-global-scope.md)

## What Users Need To Know

- `SkillsManager` is the library entry point.
- The CLI is a thin wrapper around `SkillsManager`.
- Project installs are isolated by project root.
- `--global` is the explicit shared scope.
- Built-ins support local/Git sources and `.agents/skills`.
- Plugins add new sources, targets, or extra config sources through hooks.

## What Is Intentionally Internal

Feature modules implement operations behind `SkillsManager`. They are not user
entry points. Applications should not call them directly.
