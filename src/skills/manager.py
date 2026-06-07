from __future__ import annotations

from pathlib import Path

from skills.config import Config
from skills.features.authoring import InitOptions, create_skill
from skills.features.discovery import Skill, discover_skills
from skills.features.installing import (
    InstallOptions,
    InstallResult,
    RemoveOptions,
    RemoveResult,
    UpdateOptions,
    canonical_root,
    install_from_source,
    project_lock_path,
    remove_installed,
    update_installed,
)
from skills.features.rendering import UseOptions, UseResult, render_skill
from skills.lock import LockEntry, SkillLock
from skills.plugins import PluginRegistry
from skills.project import Project
from skills.source import ParsedSource


class SkillsManager:
    """Library facade for project-scoped and global skills management."""

    def __init__(
        self,
        cwd: Path | str | None = None,
        *,
        global_config_path: Path | str | None = None,
        plugins: PluginRegistry | None = None,
    ) -> None:
        self.plugins = plugins or PluginRegistry()
        if plugins is None:
            self.plugins.load()

        config_path = Path(global_config_path) if global_config_path is not None else None
        self.project = Project.create(Path(cwd) if cwd is not None else None, global_config_path=config_path)
        self.project.hooks = self.plugins.runtime
        self.project.load_config_sources()

    def parse_source(self, source: str) -> ParsedSource:
        return self.project.require_hooks().parse_source(source)

    def list_source(self, source: Path | str = ".") -> list[Skill]:
        root = Path(source)
        if not root.is_absolute():
            root = self.project.root / root
        return discover_skills(root)

    def create(self, name: str, *, description: str) -> Path:
        return create_skill(
            self.project,
            InitOptions(
                name=name,
                description=description,
            ),
        )

    def get_config(self, key: str) -> object:
        return self.project.config.get(key)

    def set_config(self, key: str, value: object, *, local: bool = False) -> None:
        config = self.project.project_config if local else self.project.global_config
        config[key] = value

    def delete_config(self, key: str, *, local: bool = False) -> None:
        config = self.project.project_config if local else self.project.global_config
        del config[key]

    def config_values(self, *, local: bool = False) -> dict[str, object]:
        values = Config.defaults()
        values.update(self.project.global_config.data)
        if local:
            values.update(self.project.project_config.data)
        return values

    def add(
        self,
        source: str,
        *,
        skills: list[str] | None = None,
        targets: list[str] | None = None,
        mode: str | None = None,
        global_install: bool = False,
        refresh: bool = False,
    ) -> list[InstallResult]:
        return install_from_source(
            self.project,
            InstallOptions(
                source=source,
                selected_skills=skills or [],
                targets=targets or list(self.project.config.get("agents")),
                mode=mode or str(self.project.config.get("install.mode")),
                global_install=global_install,
                refresh=refresh,
            ),
        )

    def installed(self, *, global_install: bool = False) -> list[LockEntry]:
        lock = SkillLock.read(project_lock_path(self.project, global_install=global_install))
        return [entry for _, entry in sorted(lock.entries.items())]

    def remove(self, names: list[str], *, global_install: bool = False) -> list[RemoveResult]:
        return remove_installed(
            self.project,
            RemoveOptions(
                names=names,
                global_install=global_install,
            ),
        )

    def update(self, names: list[str] | None = None, *, global_install: bool = False) -> list[InstallResult]:
        return update_installed(
            self.project,
            UpdateOptions(
                names=names or [],
                global_install=global_install,
            ),
        )

    def use(
        self,
        source_or_name: str,
        *,
        skill: str | None = None,
        global_install: bool = False,
        refresh: bool = False,
    ) -> UseResult:
        return render_skill(
            self.project,
            UseOptions(
                source_or_name=source_or_name,
                skill=skill,
                global_install=global_install,
                refresh=refresh,
            ),
        )

    def lock_path(self, *, global_install: bool = False) -> Path:
        return project_lock_path(self.project, global_install=global_install)

    def installed_root(self, *, global_install: bool = False) -> Path:
        return canonical_root(self.project, global_install=global_install)
