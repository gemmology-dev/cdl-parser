"""
CDL Parser CLI.

Command-line interface for the Crystal Description Language parser.
"""

import argparse
import sys

from . import __version__
from .constants import (
    CRYSTAL_SYSTEMS,
    DEFAULT_POINT_GROUPS,
    NAMED_FORMS,
    POINT_GROUPS,
    TWIN_LAWS,
)
from .parser import parse_cdl, validate_cdl


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="cdl",
        description="Crystal Description Language (CDL) Parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s parse "cubic[m3m]:{111}"
  %(prog)s parse "cubic[m3m]:{111}@1.0 + {100}@0.3"
  %(prog)s validate "hexagonal[6/mmm]:{10-10} + {0001}"
  %(prog)s --list-point-groups
  %(prog)s --list-systems
        """,
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument(
        "command", nargs="?", choices=["parse", "validate"], help="Command to execute"
    )

    parser.add_argument("cdl", nargs="?", help="CDL string to parse/validate")

    parser.add_argument(
        "--list-point-groups", action="store_true", help="List all point groups by system"
    )

    parser.add_argument("--list-systems", action="store_true", help="List all crystal systems")

    parser.add_argument("--list-forms", action="store_true", help="List all named forms")

    parser.add_argument("--list-twins", action="store_true", help="List all twin laws")

    parser.add_argument("--json", action="store_true", help="Output parsed result as JSON")

    return parser


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # List commands
    if parsed_args.list_systems:
        print("Crystal Systems:")
        for system in sorted(CRYSTAL_SYSTEMS):
            print(f"  {system} (default: {DEFAULT_POINT_GROUPS[system]})")
        return 0

    if parsed_args.list_point_groups:
        print("Point Groups by System:")
        for system in sorted(POINT_GROUPS.keys()):
            groups = sorted(POINT_GROUPS[system])
            default = DEFAULT_POINT_GROUPS[system]
            print(f"  {system}:")
            for g in groups:
                marker = " (default)" if g == default else ""
                print(f"    {g}{marker}")
        return 0

    if parsed_args.list_forms:
        print("Named Forms:")
        for name, miller in sorted(NAMED_FORMS.items()):
            print(f"  {name:20} -> {{{miller[0]}{miller[1]}{miller[2]}}}")
        return 0

    if parsed_args.list_twins:
        print("Twin Laws:")
        for law in sorted(TWIN_LAWS):
            print(f"  {law}")
        return 0

    # Parse/validate commands require CDL string
    if not parsed_args.command or not parsed_args.cdl:
        parser.print_help()
        return 1

    if parsed_args.command == "parse":
        try:
            desc = parse_cdl(parsed_args.cdl)

            if parsed_args.json:
                import json

                print(json.dumps(desc.to_dict(), indent=2))
            else:
                print("Parsed successfully!")
                print(f"  System: {desc.system}")
                print(f"  Point Group: {desc.point_group}")
                print(f"  Forms ({len(desc.forms)}):")
                for form in desc.forms:
                    print(f"    {form.miller} @ scale={form.scale}")
                if desc.modifications:
                    print(f"  Modifications ({len(desc.modifications)}):")
                    for mod in desc.modifications:
                        print(f"    {mod}")
                if desc.twin:
                    print(f"  Twin: {desc.twin}")
                print(f"\nReconstructed: {desc}")
            return 0
        except Exception as e:
            print(f"Parse error: {e}", file=sys.stderr)
            return 1

    elif parsed_args.command == "validate":
        is_valid, error = validate_cdl(parsed_args.cdl)
        if is_valid:
            print("Valid CDL string")
            return 0
        else:
            print(f"Invalid: {error}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
