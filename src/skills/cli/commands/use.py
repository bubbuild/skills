from __future__ import annotations

import argparse

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="use",
            help="Render a skill prompt",
            description="Render SKILL.md from an installed skill or a source without installing it.",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("source_or_name", help="Installed skill name or source")
        parser.add_argument("-s", "--skill", help="Skill name when the source contains multiple skills")
        parser.add_argument("-g", "--global", dest="global_install", action="store_true", help="Use global lock")
        parser.add_argument("--refresh", action="store_true", help="Refresh remote source before rendering")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        result = manager.use(
            options.source_or_name,
            skill=options.skill,
            global_install=options.global_install,
            refresh=options.refresh,
        )
        print(result.prompt, end="" if result.prompt.endswith("\n") else "\n")
        return 0
