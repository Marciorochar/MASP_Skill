"""Command line interface for MASP routing and case ledger operations."""

import argparse
import json
import os
from pathlib import Path
import tempfile

from .case import create_case, transition_case, validate_case
from .routing import load_routing, validate_routing


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json_atomic(path: Path, value) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="masp-skill")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-routing", help="validate the routing matrix")
    validate.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    validate.add_argument("--classification", choices=("STATIC",), default="STATIC")

    new_case = commands.add_parser("new-case", help="create a case manifest")
    new_case.add_argument("--id", required=True)
    new_case.add_argument("--output", type=Path, required=True)
    new_case.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    new_case.add_argument("--high-risk", action="store_true")

    transition = commands.add_parser("transition", help="append an authorized case transition")
    transition.add_argument("--case", type=Path, required=True)
    transition.add_argument("--state", required=True)
    transition.add_argument("--actor", required=True)
    transition.add_argument("--evidence", type=Path, required=True, help="JSON file containing an evidence array")
    transition.add_argument("--phase")
    transition.add_argument("--required-classification")
    transition.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))

    validate_case_parser = commands.add_parser("validate-case", help="validate a case manifest and ledger")
    validate_case_parser.add_argument("--case", type=Path, required=True)
    validate_case_parser.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    validate_case_parser.add_argument("--root", type=Path, default=Path.cwd())

    args = parser.parse_args(argv)
    try:
        routing = load_routing(args.routing)
        if args.command == "validate-routing":
            errors = validate_routing(routing)
            if errors:
                print(f"{args.classification}: {len(errors)} erro(s)")
                for error in errors:
                    print(f"- {error}")
                return 1
            print(f"{args.classification}: 8 fases, 10 papéis, zero erros")
            return 0
        if args.command == "new-case":
            if args.output.exists():
                raise ValueError(f"refusing to overwrite existing case file {args.output}")
            case = create_case(args.id, routing, high_risk=args.high_risk)
            _write_json_atomic(args.output, case)
            print(f"SIMULATED: caso {args.id} criado em {args.output}")
            return 0
        if args.command == "transition":
            case = _read_json(args.case)
            existing_errors = validate_case(case, routing, Path.cwd())
            if existing_errors:
                raise ValueError("existing case is invalid: " + "; ".join(existing_errors))
            evidence = _read_json(args.evidence)
            if not isinstance(evidence, list):
                raise ValueError("evidence JSON must contain an array")
            result = transition_case(
                case, args.state, args.actor, evidence, routing,
                phase=args.phase, required_classification=args.required_classification,
            )
            _write_json_atomic(args.case, result)
            print(f"SIMULATED: {result['current_phase']} -> {result['state']}")
            return 0
        case = _read_json(args.case)
        errors = validate_case(case, routing, args.root)
        if errors:
            print(f"STATIC: {len(errors)} erro(s)")
            for error in errors:
                print(f"- {error}")
            return 1
        print("STATIC: caso e ledger válidos")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"{args.command}: erro: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
