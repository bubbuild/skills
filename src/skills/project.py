from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs

from skills.config import Config, ConfigSource, ConfigStack

if TYPE_CHECKING:
    from skills.plugins import PluginRuntime

PROJECT_MARKERS = ("skills.toml", "pyproject.toml")
PYPROJECT = "pyproject.toml"


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
    fallback_project_configs: list[Config]
    hooks: PluginRuntime | None = None

    @classmethod
    def create(cls, start: Path | None = None, *, global_config_path: Path | None = None) -> Project:
        root = find_project_root(start or Path.cwd())
        global_path = global_config_path or platformdirs.user_config_path("skills") / "config.toml"
        return cls(
            root=root,
            global_config=Config(global_path),
            project_config=Config(root / "skills.toml", project=True),
            fallback_project_configs=[Config(root / PYPROJECT, project=True, wrapper="tool.skills")],
        )

    @property
    def config(self) -> ConfigStack:
        return ConfigStack(self.global_config, self.project_config, self.fallback_project_configs)

    def load_config_sources(self) -> None:
        if self.hooks is None:
            return
        sources = self.hooks.config_sources(self.root)
        active, fallback = select_project_configs(sources)
        self.project_config = active
        self.fallback_project_configs = fallback

    def require_hooks(self) -> PluginRuntime:
        if self.hooks is None:
            raise ProjectHooksNotLoadedError()
        return self.hooks


class ProjectHooksNotLoadedError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("plugin runtime is not configured")


def select_project_configs(sources: list[ConfigSource]) -> tuple[Config, list[Config]]:
    if not sources:
        return Config(Path("skills.toml"), project=True), []

    active_source = sources[0]
    fallback_sources = sources[1:]
    for index, source in enumerate(sources):
        if source.exists:
            active_source = source
            fallback_sources = [] if source.blocks_lower_priority else sources[index + 1 :]
            break

    return Config.from_source(active_source), [Config.from_source(source) for source in fallback_sources]
