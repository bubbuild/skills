from __future__ import annotations

import argparse

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="installed",
            help="List installed skills from the lock file",
            description="Read the skills lock file and print installed entries.",
            aliases=("freeze",),
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-g", "--global", dest="global_install", action="store_true", help="Read global lock")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        for entry in manager.installed(global_install=options.global_install):
            targets = ",".join(entry.targets)
            print(f"{entry.name} {entry.source} {entry.content_hash} [{targets}]")
        return 0
