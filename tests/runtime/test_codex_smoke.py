import json
from pathlib import Path

from masp_skill import cli
from masp_skill.cli import _delegation_events, parse_codex_smoke_output, validate_codex_smoke_report


def test_parser_extracts_model_and_effort_from_fixture():
    parsed = parse_codex_smoke_output("Model: gpt-6.1-sol\nReasoning effort: medium\n")
    assert parsed == {"model": "gpt-6.1-sol", "effort": "medium"}


def test_parser_returns_missing_values_when_not_reported():
    assert parse_codex_smoke_output("Codex CLI 0.169.0\n") == {"model": None, "effort": None}


def test_model_divergence_is_rejected():
    report = {"classification": "RUNTIME", "expected_model": "gpt-6-luna",
              "observed_model": "gpt-6.1-sol",
              "commands": [{"command": ["codex", "--version"], "exit_code": 0, "stdout": "", "stderr": ""}]}
    assert "model mismatch: expected gpt-6-luna, observed gpt-6.1-sol" in validate_codex_smoke_report(report)


def test_runtime_requires_command_exit_code_and_streams():
    report = {"classification": "RUNTIME", "commands": [{"command": ["codex", "--version"]}]}
    errors = validate_codex_smoke_report(report)
    assert any("exit_code" in error for error in errors)
    assert any("stdout" in error for error in errors)
    assert any("stderr" in error for error in errors)


def test_not_run_does_not_require_runtime_evidence():
    assert validate_codex_smoke_report({"classification": "NOT_RUN", "commands": []}) == []


def test_delegation_claim_without_tool_event_is_not_evidence():
    stdout = '{"type":"item.completed","item":{"type":"agent_message","text":"ROLE:masp-identificador model=gpt-6-luna reasoning_effort=low"}}\n'
    event = _delegation_events(stdout, ["masp-identificador"])["masp-identificador"]
    assert event["tool_call"] is False
    assert event["completion"] is False
    assert event["observed_model"] is None


def test_runner_executes_catalog_and_attempts_runtime_smokes(tmp_path, monkeypatch):
    root = tmp_path
    (root / ".codex/agents").mkdir(parents=True)
    (root / "skills/masp").mkdir(parents=True)
    (root / ".codex/config.toml").write_text(
        '[agents]\n[agents.masp-coordenador]\nconfig_file="agents/masp-coordenador.toml"\n'
        '[agents.masp-identificador]\nconfig_file="agents/masp-identificador.toml"\n', encoding="utf-8"
    )
    (root / ".codex/agents/masp-coordenador.toml").write_text(
        'model="gpt-6.1-sol"\nmodel_reasoning_effort="medium"\n', encoding="utf-8"
    )
    (root / ".codex/agents/masp-identificador.toml").write_text(
        'model="gpt-6-luna"\nmodel_reasoning_effort="low"\n', encoding="utf-8"
    )
    (root / "skills/masp/SKILL.md").write_text("# MASP\n", encoding="utf-8")
    calls = []

    class Result:
        def __init__(self, args):
            self.returncode = 0
            self.stderr = ""
            if "--version" in args:
                self.stdout = "codex-cli 0.169.0\n"
            elif "models" in args:
                self.stdout = json.dumps({"models": [{"slug": "gpt-6.1-sol", "supported_reasoning_levels": [{"effort": "medium"}]},
                                          {"slug": "gpt-6-luna", "supported_reasoning_levels": [{"effort": "low"}]}]})
            elif "exec" in args:
                self.stdout = '{"type":"item.completed","item":{"type":"agent_message","text":"MASP_SKILL_LOADED"}}\n'
            else:
                self.stdout = "ok\n"

    def fake_run(args, **kwargs):
        calls.append(args)
        return Result(args)

    monkeypatch.setattr(cli.shutil, "which", lambda _: "codex")
    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    report = cli.run_codex_smoke(root, Path("evidence"))
    names = [check["name"] for check in report["checks"]]
    assert "model catalog" in names
    assert "MASP skill load" in names
    assert any(name.startswith("delegation masp-identificador") for name in names)
    assert any("models" in call for call in calls)
    assert any("exec" in call for call in calls)
    assert all(check["status"] != "NOT_RUN" for check in report["checks"] if check.get("classification") == "RUNTIME")

