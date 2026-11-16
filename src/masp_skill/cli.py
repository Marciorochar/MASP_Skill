"""Command line interface for static MASP routing validation."""

import argparse
from pathlib import Path

from .routing import load_routing, validate_routing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="masp-skill")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-routing", help="validate the routing matrix")
    validate.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    validate.add_argument("--classification", choices=("STATIC",), default="STATIC")
    args = parser.parse_args(argv)
    try:
        errors = validate_routing(load_routing(args.routing))
    except (OSError, ValueError) as exc:
        print(f"{args.classification}: erro ao carregar matriz: {exc}")
        return 1
    if errors:
        print(f"{args.classification}: {len(errors)} erro(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"{args.classification}: 8 fases, 10 papéis, zero erros")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
