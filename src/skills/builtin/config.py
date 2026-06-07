from __future__ import annotations

from pathlib import Path

from skills.config import ConfigSource, flatten_values, load_toml
from skills.hookspecs import hookimpl


class ConfigSourcePlugin:
    @hookimpl
    def config_sources(self, project_root: Path) -> list[ConfigSource]:
        skills_toml = project_root / "skills.toml"
        pyproject = project_root / "pyproject.toml"
        sources: list[ConfigSource] = []

        skills_data = load_toml(skills_toml)
        skills_exists = skills_toml.exists()
        sources.append(
            ConfigSource(
                name="skills.toml",
                path=skills_toml,
                data=flatten_values(skills_data),
                exists=skills_exists,
                blocks_lower_priority=skills_exists,
            )
        )

        pyproject_data = load_toml(pyproject)
        tool_skills = pyproject_data.get("tool", {}).get("skills", {})
        has_tool_skills = isinstance(tool_skills, dict)
        sources.append(
            ConfigSource(
                name="pyproject.toml:[tool.skills]",
                path=pyproject,
                data=flatten_values(tool_skills) if has_tool_skills else {},
                exists=has_tool_skills,
                wrapper="tool.skills",
            )
        )

        return sources
