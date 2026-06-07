from __future__ import annotations

import argparse
import sys

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="init",
            help="Create a SKILL.md scaffold",
            description="Create a new agent skill folder with frontmatter.",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("name", nargs="?", default="new-skill", help="Skill directory/name")
        parser.add_argument("--description", default="Describe when this skill should be used.")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        try:
            skill_file = manager.create(options.name, description=options.description)
        except FileExistsError as exc:
            print(exc, file=sys.stderr)
            return 2

        print(skill_file)
        return 0
