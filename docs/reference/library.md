# Library Reference

Use `SkillsManager` as the public library entry point.

```python
from skills import SkillsManager

manager = SkillsManager("/path/to/project")
```

## Constructor

```python
SkillsManager(cwd=None, *, global_config_path=None, plugins=None)
```

- `cwd`: project path used for root discovery.
- `global_config_path`: optional global config file path.
- `plugins`: optional preconfigured plugin registry.

## Methods

### `add(source, *, skills=None, targets=None, mode=None, global_install=False, refresh=False)`

Install skills from a source.

### `installed(*, global_install=False)`

Return lock entries in the selected scope.

### `use(source_or_name, *, skill=None, global_install=False, refresh=False)`

Render a skill from installed state or directly from a source.

### `update(names=None, *, global_install=False)`

Update installed skills. `names=None` updates all installed skills.

### `remove(names, *, global_install=False)`

Remove installed skills.

### `list_source(source=".")`

Discover skills under a local path.

### `parse_source(source)`

Parse a source string.

### `create(name, *, description)`

Create a skill scaffold.

### `lock_path(*, global_install=False)`

Return the lock path for a scope.

### `installed_root(*, global_install=False)`

Return the managed install root for a scope.
