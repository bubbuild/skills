from __future__ import annotations

from collections.abc import Iterable

from skills.features.discovery import Skill


def normalize_skill_name(name: str) -> str:
    safe = []
    previous_dash = False
    for char in name.lower():
        if char.isalnum() or char in {"_", "."}:
            safe.append(char)
            previous_dash = False
        elif not previous_dash:
            safe.append("-")
            previous_dash = True
    return "".join(safe).strip("-.")[:255] or "unnamed-skill"


def index_skills_by_normalized_name(skills: Iterable[Skill]) -> dict[str, Skill]:
    index: dict[str, Skill] = {}
    duplicates: set[str] = set()
    for skill in skills:
        name = normalize_skill_name(skill.name)
        if name in index:
            duplicates.add(name)
        else:
            index[name] = skill
    if duplicates:
        raise DuplicateSkillNameError(sorted(duplicates))
    return index


class DuplicateSkillNameError(ValueError):
    def __init__(self, names: list[str]) -> None:
        super().__init__(f"duplicate skill names after normalization: {', '.join(names)}")
