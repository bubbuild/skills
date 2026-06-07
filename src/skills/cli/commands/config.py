from __future__ import annotations

import argparse
import sys

from skills.cli.base import BaseCommand
from skills.manager import SkillsManager


class Command(BaseCommand):
    def __init__(self) -> None:
        super().__init__(
            name="config",
            help="Inspect or update skills configuration",
            description="Read and write global config or the active project skills config.",
        )

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("-l", "--local", action="store_true", help="Use active project skills configuration")
        parser.add_argument("-d", "--delete", action="store_true", help="Delete a configuration key")
        parser.add_argument("key", nargs="?", help="Configuration key")
        parser.add_argument("value", nargs="?", help="Configuration value")

    def handle(self, manager: SkillsManager, options: argparse.Namespace) -> int:
        if options.delete:
            if not options.key:
                print("config --delete requires a key", file=sys.stderr)
                return 2
            manager.delete_config(options.key, local=options.local)
            return 0
        if options.value is not None:
            if not options.key:
                print("config set requires a key", file=sys.stderr)
                return 2
            manager.set_config(options.key, options.value, local=options.local)
            return 0
        if options.key:
            print(manager.get_config(options.key))
            return 0

        for key, value in sorted(manager.config_values(local=options.local).items()):
            print(f"{key} = {value}")
        return 0
