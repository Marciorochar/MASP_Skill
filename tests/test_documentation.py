from pathlib import Path
import json
import re
import tomllib

from masp_skill.cli import main
from masp_skill.routing import load_routing, validate_routing


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROMPT = ROOT / "docs/masp/PROMPT-CODEX.md"
REPORT = ROOT / "docs/masp/RELATORIO-IMPLEMENTACAO.md"
EXAMPLE = ROOT / "docs/masp/exemplos/MASP-CONFIG-SMOKE.md"
SMOKE_JSON = ROOT / "docs/masp/evidencias/codex-smoke.json"
SMOKE_MD = ROOT / "docs/masp/evidencias/codex-smoke.md"
ROUTING = ROOT / "docs/masp/masp-routing.toml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_docs_describe_existing_commands_and_safe_case_startup():
    cli = read(ROOT / "src/masp_skill/cli.py")
    docs = read(README) + read(PROMPT) + read(ROOT / "docs/masp/LEIA-ME.md")
    for command in ("validate-routing", "new-case", "transition", "validate-case", "case-revision"):
        assert command in cli
        assert f"masp_skill.cli {command}" in docs
    assert "--id" in docs and "--output" in docs and "--root" in docs
    assert "SIMULATED" in docs and "RUNTIME" in docs and "STATIC" in docs
    for path in (README, PROMPT, EXAMPLE):
        text = read(path)
        install = text.find("python -m pip install -e")
        first_cli = text.find("python -m masp_skill.cli")
        pythonpath = text.find("PYTHONPATH=src")
        assert install >= 0 or (pythonpath >= 0 and pythonpath < first_cli), path


def test_report_inventories_roles_skills_architecture_files_tests_and_risks():
    report = read(REPORT)
    matrix = load_routing(ROUTING)
    assert len(matrix["roles"]) == 10
    assert len(matrix["phases"]) == 8
    for role, config in matrix["roles"].items():
        assert role in report
        assert config["model"] in report
        assert config["effort"] in report
    skills = {
        item["name"]
        for phase in matrix["phases"]
        for item in phase.get("skills", [])
    }
    for skill in skills:
        assert skill in report
    for heading in ("Inventário", "Arquitetura", "Arquivos", "Testes", "Riscos", "Auditoria independente"):
        assert heading.lower() in report.lower()
    assert "BLOCKED" in report
    assert "Task 7" in report
    assert "nove" in report.lower() and "masp-especialista-critico" in report
    assert "décimo" in report.lower() or "10º" in report
    smoke = json.loads(SMOKE_JSON.read_text(encoding="utf-8"))
    catalog_check = next(item for item in smoke["checks"] if item["name"] == "role model/effort catalog compatibility")
    assert catalog_check["status"] == "PASS"
    assert len(catalog_check["roles"]) == 9
    assert "masp-especialista-critico" not in catalog_check["roles"]


def test_report_classifies_runtime_from_recorded_smoke_and_does_not_claim_discovery():
    report = read(REPORT)
    example = read(EXAMPLE)
    evidence = read(SMOKE_MD)
    raw = SMOKE_JSON.read_text(encoding="utf-8")
    assert '"classification": "RUNTIME"' in raw
    assert "MASP skill load (RUNTIME): **BLOCKED**" in evidence
    assert "local agent discovery (RUNTIME): **BLOCKED**" in evidence
    assert "solicit" in report.lower() and "eventos correlacionados" in report.lower()
    assert "chamou oito papéis" not in report.lower()
    assert "LOCAL TEST" not in report
    for text in (report, example):
        assert "STATIC" in text and "SIMULATED" in text and "RUNTIME" in text
        assert "BLOCKED" in text
    assert re.search(r"(?i)discovery.{0,80}(?:pass|successful|sucesso)", report) is None
    assert "modelo efetivo" in report.lower() or "modelo/effort efetivo" in report.lower()


def test_documentation_has_no_placeholder_and_routing_still_validates(capsys):
    for path in (README, PROMPT, REPORT, EXAMPLE):
        assert "TODO" not in read(path)
        assert "<CAMINHO-" not in read(path)
    assert validate_routing(load_routing(ROUTING)) == []
    assert main(["validate-routing", "--routing", str(ROUTING), "--classification", "STATIC"]) == 0
    assert "STATIC" in capsys.readouterr().out
