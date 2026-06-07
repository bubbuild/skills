# Plugin Reference

Plugins extend sources, install targets, or config formats.

Register plugins through the `skills` entry point group:

```toml
[project.entry-points."skills"]
my_plugin = "my_package:Plugin"
```

Use `hookimpl`:

```python
from pathlib import Path

from skills import hookimpl


class Plugin:
    @hookimpl
    def install_target(self, name, project, global_install) -> Path | None:
        if name != "codex":
            return None
        if global_install:
            return Path("~/.codex/skills").expanduser()
        return project.root / ".codex" / "skills"
```

## Hooks

- `parse_source(raw)`: parse a source string.
- `fetch_source(source, project, refresh)`: return a fetched local source tree.
- `install_target(name, project, global_install)`: return a target directory.
- `config_sources(project_root)`: return project config sources in priority order.
