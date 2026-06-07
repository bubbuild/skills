from __future__ import annotations

import importlib.metadata
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pluggy

from skills.config import ConfigSource
from skills.hookspecs import SKILLS_HOOK_NAMESPACE, SkillsHookSpecs
from skills.source import FetchedSource, ParsedSource

if TYPE_CHECKING:
    from skills.features.discovery import Skill


@dataclass(frozen=True)
class PluginStatus:
    is_success: bool
    detail: str | None = None


class PluginRuntime:
    def __init__(self, manager: pluggy.PluginManager) -> None:
        self.manager = manager

    def parse_source(self, raw: str) -> ParsedSource:
        source = self.manager.hook.parse_source(raw=raw)
        if source is None:
            raise UnsupportedSourceError(raw)
        return cast(ParsedSource, source)

    def fetch_source(self, source: ParsedSource, project: Any, *, refresh: bool = False) -> FetchedSource:
        fetched = self.manager.hook.fetch_source(source=source, project=project, refresh=refresh)
        if fetched is None:
            raise UnsupportedFetchError(source.kind)
        return cast(FetchedSource, fetched)

    def install_target(self, name: str, project: Any, *, global_install: bool = False) -> Path:
        target = self.manager.hook.install_target(name=name, project=project, global_install=global_install)
        if target is None:
            raise UnsupportedTargetError(name)
        return cast(Path, target)

    def config_sources(self, project_root: Path) -> list[ConfigSource]:
        groups = self.manager.hook.config_sources(project_root=project_root)
        sources: list[ConfigSource] = []
        for group in groups:
            sources.extend(cast(list[ConfigSource], group))
        return sources

    def render_prompt(self, skill: Skill, prompt: str, project: Any) -> str:
        rendered = self.manager.hook.render_prompt(skill=skill, prompt=prompt, project=project)
        if rendered is None:
            return prompt
        return cast(str, rendered)


class UnsupportedSourceError(ValueError):
    def __init__(self, raw: str) -> None:
        super().__init__(f"unsupported source: {raw}")


class UnsupportedFetchError(ValueError):
    def __init__(self, kind: str) -> None:
        super().__init__(f"no plugin can fetch source kind: {kind}")


class UnsupportedTargetError(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"unsupported install target: {name}")


class PluginRegistry:
    def __init__(self) -> None:
        self.manager = pluggy.PluginManager(SKILLS_HOOK_NAMESPACE)
        self.manager.add_hookspecs(SkillsHookSpecs)
        self.status: dict[str, PluginStatus] = {}
        self.runtime = PluginRuntime(self.manager)

    def load(self) -> None:
        self._load_builtin_plugins()
        self._load_entrypoint_plugins()

    def _register(self, plugin: object, name: str) -> None:
        try:
            self.manager.register(plugin, name=name)
        except Exception as exc:
            self.status[name] = PluginStatus(is_success=False, detail=str(exc))
        else:
            self.status[name] = PluginStatus(is_success=True)

    def _load_builtin_plugins(self) -> None:
        from skills.builtin.agents import AgentsTargetPlugin
        from skills.builtin.git import GitSourcePlugin

        self._register(GitSourcePlugin(), "builtin.git")
        self._register(AgentsTargetPlugin(), "builtin.agents")

    def _load_entrypoint_plugins(self) -> None:
        for entry_point in importlib.metadata.entry_points(group=SKILLS_HOOK_NAMESPACE):
            try:
                plugin = entry_point.load()
                if callable(plugin):
                    plugin = plugin()
            except Exception as exc:
                self.status[entry_point.name] = PluginStatus(is_success=False, detail=str(exc))
                continue
            self._register(plugin, entry_point.name)
