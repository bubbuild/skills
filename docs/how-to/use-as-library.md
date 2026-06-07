# Use Skills As A Library

Use `SkillsManager` when an application needs built-in skills management.

```python
from skills import SkillsManager

manager = SkillsManager("/path/to/project")
manager.add("./my-skills", skills=["code-review"], mode="copy")

prompt = manager.use("code-review").prompt
installed = manager.installed()
```

## Manage Project Skills

```python
manager.add("./my-skills", skills=["code-review"])
manager.update(["code-review"])
manager.remove(["code-review"])
```

Project installs are scoped to the project root:

```python
manager.lock_path()
manager.installed_root()
```

## Use Global Skills

Pass `global_install=True` only when the skill should be shared globally:

```python
manager.add("./my-skills", skills=["code-review"], global_install=True)
manager.use("code-review", global_install=True)
```

## Discover Skills Without Installing

```python
skills = manager.list_source("./my-skills")
```

## Parse A Source

```python
source = manager.parse_source("openai/skills@main")
```

Use this for inspection or UI previews before installing.
