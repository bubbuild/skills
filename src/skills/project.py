from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs

from skills.config import Config, ConfigStack

if TYPE_CHECKING:
    from skills.plugins import PluginRuntime

PROJECT_MARKERS = ("skills.toml",)


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in PROJECT_MARKERS):
            return candidate
    return current


@dataclass
class Project:
    root: Path
    global_config: Config
    project_config: Config
    plugin_project_configs: list[Config]
    hooks: PluginRuntime | None = None

    @classmethod
    def create(cls, start: Path | None = None, *, global_config_path: Path | None = None) -> Project:
        root = find_project_root(start or Path.cwd())
        global_path = global_config_path or platformdirs.user_config_path("skills") / "config.toml"
        return cls(
            root=root,
            global_config=Config(global_path),
            project_config=Config(root / "skills.toml", project=True),
            plugin_project_configs=[],
        )

    @property
    def config(self) -> ConfigStack:
        return ConfigStack(self.global_config, self.project_config, self.plugin_project_configs)

    def load_config_sources(self) -> None:
        if self.hooks is None:
            return
        self.plugin_project_configs = [
            Config.from_source(source) for source in self.hooks.config_sources(self.root) if source.exists
        ]

    def require_hooks(self) -> PluginRuntime:
        if self.hooks is None:
            raise ProjectHooksNotLoadedError()
        return self.hooks


class ProjectHooksNotLoadedError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("plugin runtime is not configured")
