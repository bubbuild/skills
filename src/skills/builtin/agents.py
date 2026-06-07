from __future__ import annotations

from pathlib import Path

from skills.hookspecs import hookimpl
from skills.project import Project


class AgentsTargetPlugin:
    @hookimpl
    def install_target(self, name: str, project: Project, global_install: bool) -> Path | None:
        if name != "agents":
            return None
        if global_install:
            return Path("~/.agents/skills").expanduser()
        return project.root / ".agents" / "skills"
