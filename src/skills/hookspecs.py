from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pluggy

from skills.config import ConfigSource
from skills.source import FetchedSource, ParsedSource

if TYPE_CHECKING:
    from skills.project import Project

SKILLS_HOOK_NAMESPACE = "skills"
hookspec = pluggy.HookspecMarker(SKILLS_HOOK_NAMESPACE)
hookimpl = pluggy.HookimplMarker(SKILLS_HOOK_NAMESPACE)


class SkillsHookSpecs:
    @hookspec(firstresult=True)
    def parse_source(self, raw: str) -> ParsedSource | None:
        """Parse a source string into a provider-specific normalized source."""
        raise NotImplementedError

    @hookspec(firstresult=True)
    def fetch_source(self, source: ParsedSource, project: Project, refresh: bool) -> FetchedSource | None:
        """Fetch or locate a parsed source and return its local tree and resolved state."""
        raise NotImplementedError

    @hookspec(firstresult=True)
    def install_target(self, name: str, project: Project, global_install: bool) -> Path | None:
        """Return the skills directory for an install target name."""
        raise NotImplementedError

    @hookspec
    def config_sources(self, project_root: Path) -> list[ConfigSource]:
        """Return extra project configuration sources below skills.toml."""
        raise NotImplementedError
