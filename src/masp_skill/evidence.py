"""Evidence records and reference validation for MASP cases."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

CLASSIFICATIONS = {"STATIC", "SIMULATED", "RUNTIME", "NOT_RUN"}


def make_evidence(
    path: Path,
    root: Path,
    *,
    classification: str,
    description: str,
    evidence_id: str | None = None,
    **metadata: Any,
) -> dict[str, Any]:
    """Build a reference to an existing file, relative to root when possible."""
    path, root = Path(path).resolve(), Path(root).resolve()
    try:
        reference = path.relative_to(root).as_posix()
    except ValueError:
        reference = str(path)
    return {
        "id": evidence_id or hashlib.sha256(str(path).encode()).hexdigest()[:16],
        "path": reference,
        "classification": classification,
        "description": description,
        **metadata,
    }


def validate_evidence(evidence: list[dict[str, Any]], root: Path) -> list[str]:
    """Return errors for malformed or missing evidence references."""
    root = Path(root).resolve()
    if not isinstance(evidence, list):
        return ["evidence must be an array"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(evidence):
        label = f"evidence {index + 1}"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        evidence_id, reference = item.get("id"), item.get("path")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            errors.append(f"{label} is missing id")
        elif evidence_id in seen:
            errors.append(f"duplicate evidence id {evidence_id}")
        else:
            seen.add(evidence_id)
        if not isinstance(reference, str) or not reference.strip():
            errors.append(f"{label} is missing path")
            continue
        path = Path(reference)
        resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            errors.append(f"{label} path escapes evidence root {root}: {reference}")
            continue
        if not resolved.is_file():
            errors.append(f"{label} references missing file {reference}")
        classification = item.get("classification")
        if classification not in CLASSIFICATIONS:
            errors.append(f"{label} has invalid classification {classification!r}")
        if not isinstance(item.get("description"), str) or not item["description"].strip():
            errors.append(f"{label} is missing description")
    return errors
