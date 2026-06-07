from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from skills.project import Project

TEMPLATE = """---
name: {name}
description: {description}
---

# {title}

Use this skill when ...
"""


@dataclass(frozen=True)
class InitOptions:
    name: str
    description: str


def create_skill(project: Project, options: InitOptions) -> Path:
    directory = Path(options.name)
    if not directory.is_absolute():
        directory = project.root / directory
    directory.mkdir(parents=True, exist_ok=True)
    skill_file = directory / "SKILL.md"
    if skill_file.exists():
        raise SkillAlreadyExistsError(skill_file)

    title = options.name.replace("-", " ").replace("_", " ").title()
    skill_file.write_text(
        TEMPLATE.format(name=options.name, description=options.description, title=title),
        encoding="utf-8",
    )
    return skill_file


class SkillAlreadyExistsError(FileExistsError):
    def __init__(self, path: Path) -> None:
        super().__init__(f"{path} already exists")
        self.path = path
