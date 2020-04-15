# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Hadrien Chauvin

"""Command-Line Interface."""

import argparse
import sys
import os

from buildcache import Cache


class CLI:
    """
    Command-Line Interface.
    """

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='CircleCI-like local cache', usage="buildcache <command> [<args>]")
        subcommands = [
            attr for attr in dir(self)
            if not attr.startswith("_") and callable(getattr(self, attr))
        ]
        parser.add_argument(
            'command',
            help='Subcommand to run: one of: ' + " ".join(subcommands))
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def restore(self):
        parser = argparse.ArgumentParser(
            description='Restore a cache')
        parser.add_argument('keys', help='Cache keys to search for', nargs='*')
        args = parser.parse_args(sys.argv[2:])
        self._cache().restore(args.keys)

    def save(self):
        parser = argparse.ArgumentParser(
            description='Save files into a cache')
        parser.add_argument('key', help='Cache key')
        parser.add_argument('paths', help='Paths to save', nargs='*')
        args = parser.parse_args(sys.argv[2:])
        self._cache().save(args.key, args.paths)

    def checksum(self):
        parser = argparse.ArgumentParser(
            description='Checksum files or directories')
        parser.add_argument('paths', help='Paths to get a checksum for', nargs='*')
        args = parser.parse_args(sys.argv[2:])
        print(self._cache().checksum(args.paths), end="")

    def _cache(self):
        return Cache(
            workdir=os.getcwd(),
            cachedir=os.path.join(os.getcwd(), ".cache")
        )

try:
    CLI()
except KeyboardInterrupt as e:
    print("Interrupted")
    sys.exit(1)
