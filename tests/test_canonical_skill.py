"""The Codex-discovered MASP skill must be the canonical, complete entrypoint."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / ".agents/skills/masp/SKILL.md"
LEGACY = ROOT / "skills/masp/SKILL.md"
GUIDE = ROOT / "skills/masp/references/routing-guide.md"

PHASES = ["Identificação", "Observação", "Análise", "Plano de ação", "Ação", "Verificação", "Padronização", "Conclusão"]
STATES = ["PENDING", "IN_PROGRESS", "PASS", "FAIL", "BLOCKED", "NOT_RUN"]
COMMANDS = ["validate-routing", "new-case", "transition", "case-revision", "validate-case"]


def test_discovered_skill_is_complete_and_references_existing_guide():
    text = CANONICAL.read_text(encoding="utf-8")
    assert re.search(r"(?m)^name:\s*masp\s*$", text)
    assert re.search(r"(?m)^description:\s*Use when ", text)
    for value in (*PHASES, *STATES, *COMMANDS):
        assert value in text, value
    assert "superpowers:" in text
    guide_ref = "../../../skills/masp/references/routing-guide.md"
    assert guide_ref in text
    assert (CANONICAL.parent / guide_ref).resolve() == GUIDE.resolve()
    assert GUIDE.is_file()


def test_legacy_skill_is_a_forwarding_stub_not_competing_instructions():
    old = LEGACY.read_text(encoding="utf-8")
    assert ".agents/skills/masp/SKILL.md" in old
    assert "compatibilidade" in old.lower()
    assert len(old) < 1400
