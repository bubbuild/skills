from __future__ import annotations

import argparse

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="remove",
            help="Remove installed skills",
            description="Remove installed skills from targets, canonical storage, and the lock file.",
            aliases=("rm",),
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("skills", nargs="+", help="Installed skill names, or '*' for all")
        parser.add_argument("-g", "--global", dest="global_install", action="store_true", help="Remove globally")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        results = manager.remove(options.skills, global_install=options.global_install)
        for result in results:
            print(result.name)
        return 0
