from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    description: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text

    metadata: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")
    return metadata, text[end + 4 :].lstrip()


def read_skill(path: Path) -> Skill:
    skill_file = path if path.name == "SKILL.md" else path / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")
    metadata, body = _parse_frontmatter(text)
    name = metadata.get("name") or skill_file.parent.name
    description = metadata.get("description")
    if description is None:
        for line in body.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                description = stripped
                break
    return Skill(name=name, path=skill_file.parent, description=description, metadata=metadata)


def discover_skills(root: Path) -> list[Skill]:
    if root.name == "SKILL.md":
        return [read_skill(root)]
    if (root / "SKILL.md").exists():
        return [read_skill(root)]
    return sorted(
        (read_skill(path) for path in root.rglob("SKILL.md")),
        key=lambda skill: skill.name,
    )
