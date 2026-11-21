"""CLI ergonomics: record-evidence and status. No Codex inference; commands run are local Python one-liners."""
import json
from pathlib import Path
import sys

import pytest

from masp_skill.case import GATE_REQUIREMENTS, case_revision, validate_case
from masp_skill.cli import main
from masp_skill.ergonomics import parse_meta
from masp_skill.evidence import validate_evidence
from masp_skill.routing import load_routing

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "masp" / "masp-routing.toml"
ROUTING = load_routing(MATRIX)


def _record(tmp_path, *extra, output="ev.json"):
    return main(["record-evidence", "--output", output, "--root", str(tmp_path), *extra])


def _artifact(tmp_path, name="note.md", text="observed\n"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return name


def test_record_file_evidence_with_gate_hash_and_append(tmp_path, capsys):
    note = _artifact(tmp_path)
    assert _record(tmp_path, "--file", note, "--classification", "STATIC", "--description", "first",
                   "--id", "e1", "--gate", "identificacao", "--satisfies", "extra_one") == 0
    assert _record(tmp_path, "--file", note, "--classification", "SIMULATED", "--description", "second",
                   "--id", "e2") == 0
    capsys.readouterr()
    data = json.loads((tmp_path / "ev.json").read_text(encoding="utf-8"))
    assert [item["id"] for item in data] == ["e1", "e2"]
    assert set(data[0]["satisfies"]) == GATE_REQUIREMENTS["identificacao"] | {"extra_one"}
    assert validate_evidence(data, tmp_path) == []


def test_duplicate_id_is_refused_and_reset_starts_over(tmp_path, capsys):
    note = _artifact(tmp_path)
    args = ("--file", note, "--classification", "STATIC", "--description", "d", "--id", "same")
    assert _record(tmp_path, *args) == 0
    assert _record(tmp_path, *args) == 1
    assert "already exists" in capsys.readouterr().out
    assert _record(tmp_path, *args, "--reset") == 0
    assert len(json.loads((tmp_path / "ev.json").read_text(encoding="utf-8"))) == 1


def test_command_is_recorded_as_runtime_with_real_exit_code_and_log(tmp_path, capsys):
    assert _record(tmp_path, "--description", "ran", "--id", "run1", "--meta", "role=masp-testador",
                   "--", sys.executable, "-c", "print('ok')") == 0
    capsys.readouterr()
    record = json.loads((tmp_path / "ev.json").read_text(encoding="utf-8"))[0]
    assert record["classification"] == "RUNTIME"
    assert record["exit_code"] == 0 and record["stdout"].strip() == "ok"
    assert record["role"] == "masp-testador"
    assert (tmp_path / record["path"]).is_file()
    assert validate_evidence([record], tmp_path) == []


def test_failing_command_is_recorded_honestly_not_hidden(tmp_path, capsys):
    assert _record(tmp_path, "--description", "fails", "--",
                   sys.executable, "-c", "import sys; sys.exit(3)") == 0
    capsys.readouterr()
    assert json.loads((tmp_path / "ev.json").read_text(encoding="utf-8"))[0]["exit_code"] == 3


def test_missing_command_and_timeout_record_nothing(tmp_path, capsys):
    assert _record(tmp_path, "--description", "nope", "--", "definitely-not-a-real-binary-xyz") == 1
    assert _record(tmp_path, "--description", "slow", "--timeout", "1", "--",
                   sys.executable, "-c", "import time; time.sleep(30)") == 1
    capsys.readouterr()
    assert not (tmp_path / "ev.json").exists()


def test_command_rejects_non_runtime_classification_and_file_needs_classification(tmp_path, capsys):
    assert _record(tmp_path, "--description", "x", "--classification", "STATIC", "--",
                   sys.executable, "-c", "pass") == 1
    note = _artifact(tmp_path)
    assert _record(tmp_path, "--description", "x", "--file", note) == 1
    capsys.readouterr()


def test_paths_must_stay_inside_root(tmp_path, capsys):
    outside = tmp_path.parent / "outside-note.md"
    outside.write_text("x", encoding="utf-8")
    assert main(["record-evidence", "--output", "../escape.json", "--root", str(tmp_path), "--description", "x",
                 "--file", _artifact(tmp_path), "--classification", "STATIC"]) == 1
    assert _record(tmp_path, "--description", "x", "--file", str(outside), "--classification", "STATIC") == 1
    capsys.readouterr()


def test_parse_meta_decodes_json_and_rejects_reserved_keys():
    assert parse_meta(["role=masp-testador", 'related_evidence=["a","b"]', "n=3"]) == {
        "role": "masp-testador", "related_evidence": ["a", "b"], "n": 3}
    with pytest.raises(ValueError):
        parse_meta(["exit_code=0"])
    with pytest.raises(ValueError):
        parse_meta(["novalue"])


def test_workflow_new_case_record_status_transition_without_hand_written_json(tmp_path, capsys):
    case_path = tmp_path / "case.json"
    common = ["--routing", str(MATRIX), "--root", str(tmp_path)]
    assert main(["new-case", "--id", "MASP-ERGO", "--output", "case.json", *common]) == 0
    capsys.readouterr()

    assert main(["status", "--case", "case.json", *common]) == 0
    out = capsys.readouterr().out
    assert "Estado: PENDING" in out and "Identificação" in out
    assert f"--expected-revision {case_revision(case_path.read_bytes())}" in out

    note = _artifact(
        tmp_path,
        "id.md",
        "# Identificação\n"
        "- Problema: falha intermitente de cálculo.\n"
        "- Impacto: divergência de centavos na fatura.\n"
        "- Escopo: módulo de faturamento local.\n"
        "- Exclusões: gateway de pagamento externo.\n"
        "- Métrica de sucesso: 100% dos testes aprovados.\n",
    )
    assert _record(tmp_path, "--file", note, "--classification", "STATIC", "--description", "start",
                   "--id", "start", "--reset", output="start.json") == 0
    revision = case_revision(case_path.read_bytes())
    assert main(["transition", "--case", "case.json", "--state", "IN_PROGRESS", "--actor", "masp-coordenador",
                 "--evidence", "start.json", "--expected-revision", revision, *common]) == 0

    assert _record(tmp_path, "--file", note, "--classification", "STATIC", "--description", "gate",
                   "--id", "gate", "--gate", "identificacao", "--reset", output="pass.json") == 0
    capsys.readouterr()
    assert main(["status", "--case", "case.json", *common]) == 0
    assert "Estado: IN_PROGRESS" in capsys.readouterr().out
    revision = case_revision(case_path.read_bytes())
    assert main(["transition", "--case", "case.json", "--state", "PASS", "--actor", "masp-coordenador",
                 "--evidence", "pass.json", "--expected-revision", revision, *common]) == 0

    capsys.readouterr()
    assert main(["status", "--case", "case.json", *common]) == 0
    out = capsys.readouterr().out
    assert "Estado: PASS" in out and '--phase "Observação"' in out
    assert validate_case(json.loads(case_path.read_text(encoding="utf-8")), ROUTING, tmp_path) == []
