"""Command line interface for MASP routing and case ledger operations."""

import argparse
import json
import os
from pathlib import Path
import tempfile
from contextlib import contextmanager

from .case import case_revision, create_case, transition_case, validate_case
from .routing import load_routing, validate_routing


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _within_root(path: Path, root: Path) -> Path:
    resolved_root = Path(root).resolve()
    candidate = Path(path)
    resolved_path = (candidate if candidate.is_absolute() else resolved_root / candidate).resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"path {path} escapes workspace root {resolved_root}") from exc
    return resolved_path


@contextmanager
def _case_lock(path: Path):
    """Serialize writers through a persistent sidecar lock on Windows and POSIX."""
    lock_path = path.resolve().with_name(path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    stream = lock_path.open("a+b")
    locked = False
    try:
        if os.name == "nt":
            import msvcrt
            stream.seek(0, os.SEEK_END)
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        locked = True
        yield
    finally:
        if locked and os.name == "nt":
            import msvcrt
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        elif locked:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        stream.close()


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

    new_case = commands.add_parser("new-case", help="create a simulated case manifest")
    new_case.add_argument("--id", required=True)
    new_case.add_argument("--output", type=Path, required=True)
    new_case.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    new_case.add_argument("--high-risk", action="store_true")
    new_case.add_argument("--root", type=Path, default=Path.cwd())

    transition = commands.add_parser("transition", help="append a simulated case transition")
    transition.add_argument("--case", type=Path, required=True)
    transition.add_argument("--state", required=True)
    transition.add_argument("--actor", required=True)
    transition.add_argument("--evidence", type=Path, required=True, help="JSON file containing an evidence array")
    transition.add_argument("--phase")
    transition.add_argument("--required-classification")
    transition.add_argument("--routing", type=Path, default=Path("docs/masp/masp-routing.toml"))
    transition.add_argument("--expected-revision", required=True, help="SHA-256 returned by case-revision")
    transition.add_argument("--root", type=Path, default=Path.cwd(), help="workspace root for evidence references")

    revision = commands.add_parser("case-revision", help="print the current manifest revision for compare-and-swap")
    revision.add_argument("--case", type=Path, required=True)

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
            case = create_case(args.id, routing, high_risk=args.high_risk)
            output_path = _within_root(args.output, args.root)
            with _case_lock(output_path):
                if output_path.exists():
                    raise ValueError(f"refusing to overwrite existing case file {output_path}")
                _write_json_atomic(output_path, case)
            print(f"SIMULATED: caso {args.id} criado em {output_path}; actor and model identities are not authenticated")
            return 0
        if args.command == "transition":
            case_path = _within_root(args.case, args.root)
            evidence_path = _within_root(args.evidence, args.root)
            with _case_lock(case_path):
                raw = case_path.read_bytes()
                revision_now = case_revision(raw)
                if revision_now != args.expected_revision:
                    raise ValueError(f"stale case revision; current={revision_now}")
                case = json.loads(raw.decode("utf-8-sig"))
                existing_errors = validate_case(case, routing, args.root)
                if existing_errors:
                    raise ValueError("existing case is invalid: " + "; ".join(existing_errors))
                evidence = _read_json(evidence_path)
                if not isinstance(evidence, list):
                    raise ValueError("evidence JSON must contain an array")
                result = transition_case(
                    case, args.state, args.actor, evidence, routing,
                    phase=args.phase, required_classification=args.required_classification,
                    root=args.root,
                )
                _write_json_atomic(case_path, result)
            print(f"SIMULATED: {result['current_phase']} -> {result['state']}; role and approval labels are not authenticated")
            return 0
        if args.command == "case-revision":
            print(f"SHA256: {case_revision(args.case.read_bytes())}")
            return 0
        case_path = _within_root(args.case, args.root)
        case = _read_json(case_path)
        errors = validate_case(case, routing, args.root)
        if errors:
            print(f"STATIC: {len(errors)} erro(s)")
            for error in errors:
                print(f"- {error}")
            return 1
        print(f"STATIC: caso e ledger válidos; revision={case_revision(case_path.read_bytes())}")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"{args.command}: erro: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
