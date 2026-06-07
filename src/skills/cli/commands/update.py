from __future__ import annotations

import argparse

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="update",
            help="Update installed skills",
            description="Re-fetch locked sources and reinstall matching skills.",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("skills", nargs="*", help="Installed skill names; defaults to all")
        parser.add_argument("-g", "--global", dest="global_install", action="store_true", help="Update globally")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        results = manager.update(options.skills, global_install=options.global_install)
        for result in results:
            print(result.lock_entry.name)
        return 0
