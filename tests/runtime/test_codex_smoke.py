from masp_skill.cli import parse_codex_smoke_output, validate_codex_smoke_report


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

