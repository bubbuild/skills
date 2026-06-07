# Use The CLI

The CLI wraps `SkillsManager`. Use it for shell workflows.

## Install From A Local Directory

```bash
skills add ./my-skills --skill code-review
```

Use copy mode instead of symlinks:

```bash
skills add ./my-skills --skill code-review --copy
```

## Install From GitHub

```bash
skills add openai/skills@main --skill code-review
skills add gh:openai/skills@main --skill code-review
```

## Render A Skill

Installed skill:

```bash
skills use code-review
```

Skill from a source without installing:

```bash
skills use ./my-skills --skill code-review
```

## Update Or Remove

```bash
skills update code-review
skills remove code-review
```

Update all installed skills in the current scope:

```bash
skills update
```
