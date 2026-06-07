from __future__ import annotations

import argparse

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="list",
            help="List skills in a local directory",
            description="Discover SKILL.md files and print their names and descriptions.",
            aliases=("ls",),
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("path", nargs="?", default=".", help="Directory, skill folder, or SKILL.md")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        for skill in manager.list_source(options.path):
            description = f" - {skill.description}" if skill.description else ""
            print(f"{skill.name}{description}")
        return 0
