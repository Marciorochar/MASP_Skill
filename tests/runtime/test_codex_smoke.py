import json
from pathlib import Path

from masp_skill import cli
from masp_skill.cli import (_delegation_events, _skill_load_evidence, parse_codex_smoke_output,
                            validate_codex_smoke_report)


def test_text_claims_do_not_verify_effective_model_or_effort():
    parsed = parse_codex_smoke_output("Model: gpt-6.1-sol\nReasoning effort: medium\n")
    assert parsed == {"model": None, "effort": None}


def test_runtime_smoke_strict_returns_nonzero_for_blocked_mandatory_check(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "run_codex_smoke", lambda root, output: {
        "classification": "NOT_RUN", "checks": [{"name": "CLI", "status": "BLOCKED"}],
    })
    assert cli.main(["runtime-smoke", "--root", str(tmp_path), "--output-dir", str(tmp_path / "out"), "--strict"]) == 1
    capsys.readouterr()


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


def test_null_exit_code_is_only_valid_when_process_did_not_complete():
    report = {"classification": "RUNTIME", "commands": [{"command": ["codex"], "process_completed": True,
              "exit_code": None, "stdout": "", "stderr": ""}]}
    assert any("completed without an integer exit_code" in error for error in validate_codex_smoke_report(report))


def test_not_run_does_not_require_runtime_evidence():
    assert validate_codex_smoke_report({"classification": "NOT_RUN", "commands": []}) == []


def test_delegation_claim_without_tool_event_is_not_evidence():
    stdout = '{"type":"item.completed","item":{"type":"agent_message","text":"ROLE:masp-identificador model=gpt-6-luna reasoning_effort=low"}}\n'
    event = _delegation_events(stdout, ["masp-identificador"])["masp-identificador"]
    assert event["tool_call"] is False
    assert event["completion"] is False
    assert event["observed_model"] is None


def test_delegation_requires_correlated_structured_call_agent_and_completion_events():
    events = [
        {"type": "item.started", "item": {"type": "collab_tool_call", "tool": "spawn_agent",
         "call_id": "call-1", "agent_name": "masp-identificador", "status": "in_progress"}},
        {"type": "item.started", "item": {"type": "agent_started", "call_id": "call-1", "agent_id": "agent-1",
         "agent_name": "masp-identificador", "status": "in_progress"}},
        {"type": "item.completed", "item": {"type": "agent_completed", "call_id": "call-1", "agent_id": "agent-1",
         "status": "completed", "effective_model": "gpt-6-luna",
         "effective_effort": "low"}},
    ]
    stdout = "\n".join(json.dumps(event) for event in events)
    result = _delegation_events(stdout, ["masp-identificador"])["masp-identificador"]
    assert result["tool_call"] is True
    assert result["completion"] is True
    assert result["observed_model"] == "gpt-6-luna"
    assert result["observed_effort"] == "low"


def test_unmatched_call_and_agent_ids_do_not_prove_delegation():
    events = [
        {"type": "item.started", "item": {"type": "collab_tool_call", "tool": "spawn_agent",
         "call_id": "call-1", "agent_name": "masp-identificador", "status": "in_progress"}},
        {"type": "item.started", "item": {"type": "agent_started", "call_id": "call-other", "agent_id": "agent-1",
         "agent_name": "masp-identificador", "status": "in_progress"}},
        {"type": "item.completed", "item": {"type": "agent_completed", "call_id": "call-1", "agent_id": "agent-other",
         "agent_name": "masp-identificador", "status": "completed", "effective_model": "gpt-6-luna",
         "effective_effort": "low"}},
    ]
    result = _delegation_events("\n".join(json.dumps(event) for event in events), ["masp-identificador"])["masp-identificador"]
    assert result["tool_call"] is False
    assert result["completion"] is False
    assert result["observed_model"] is None


def test_assistant_skill_marker_is_not_structured_load_evidence():
    stdout = '{"type":"item.completed","item":{"type":"agent_message","text":"MASP_SKILL_LOADED"}}\n'
    assert _skill_load_evidence(stdout) is None


def test_structured_skill_load_event_is_evidence():
    stdout = json.dumps({"type": "item.completed", "item": {"type": "skill_load", "skill_name": "masp",
                                                            "status": "loaded"}})
    assert _skill_load_evidence(stdout)["skill_name"] == "masp"


def test_timeout_is_a_blocked_command_and_report_persists(tmp_path, monkeypatch):
    root = tmp_path
    (root / ".codex/agents").mkdir(parents=True)
    (root / "skills/masp").mkdir(parents=True)
    (root / ".codex/config.toml").write_text('[agents]\n', encoding="utf-8")
    (root / "skills/masp/SKILL.md").write_text("# MASP\n", encoding="utf-8")

    def timeout_run(args, **kwargs):
        if "exec" in args:
            raise cli.subprocess.TimeoutExpired(args, 1, output=b"partial bytes", stderr=b"timeout bytes")
        class Result:
            returncode = 0
            stdout = "ok"
            stderr = ""
        return Result()

    monkeypatch.setattr(cli.shutil, "which", lambda _: "codex")
    monkeypatch.setattr(cli.subprocess, "run", timeout_run)
    report = cli.run_codex_smoke(root, Path("evidence"))
    blocked = report["commands"][-1]
    assert blocked["process_completed"] is False
    assert blocked["exit_code"] is None
    assert blocked["stdout"] == "partial bytes"
    assert blocked["stderr"] == "timeout bytes"
    assert (root / "evidence/codex-smoke.json").is_file()
    assert (root / "evidence/codex-smoke.md").is_file()
    assert validate_codex_smoke_report(report) == []


def test_process_launch_failure_is_blocked_and_persisted(tmp_path, monkeypatch):
    root = tmp_path
    (root / ".codex/agents").mkdir(parents=True)
    (root / "skills/masp").mkdir(parents=True)
    (root / ".codex/config.toml").write_text('[agents]\n', encoding="utf-8")
    (root / "skills/masp/SKILL.md").write_text("# MASP\n", encoding="utf-8")

    def failed_run(args, **kwargs):
        if "exec" in args:
            raise OSError("process launch failed")
        class Result:
            returncode = 0
            stdout = "ok"
            stderr = ""
        return Result()

    monkeypatch.setattr(cli.shutil, "which", lambda _: "codex")
    monkeypatch.setattr(cli.subprocess, "run", failed_run)
    report = cli.run_codex_smoke(root, Path("evidence"))
    failed = report["commands"][-1]
    assert failed["process_completed"] is False
    assert failed["exit_code"] is None
    assert failed["stderr"] == "process launch failed"
    assert next(check for check in report["checks"] if check["name"] == "MASP skill load")["status"] == "BLOCKED"
    assert (root / "evidence/codex-smoke.json").is_file()
    assert (root / "evidence/codex-smoke.md").is_file()
    assert validate_codex_smoke_report(report) == []


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
    assert next(check for check in report["checks"] if check["name"] == "MASP skill load")["status"] == "BLOCKED"

