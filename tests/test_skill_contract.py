from pathlib import Path
import re
import tomllib

from masp_skill.routing import load_routing


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "masp" / "SKILL.md"
REFERENCE = ROOT / "skills" / "masp" / "references" / "routing-guide.md"
ROUTING = ROOT / "docs" / "masp" / "masp-routing.toml"


def test_skill_has_discoverable_frontmatter_and_trigger_description():
    text = SKILL.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    assert frontmatter, "SKILL.md must begin with YAML frontmatter"
    fields = dict(
        line.split(":", 1)
        for line in frontmatter.group(1).splitlines()
        if ":" in line
    )
    assert fields.get("name", "").strip() == "masp"
    description = fields.get("description", "").strip()
    assert description.startswith("Use when ")
    assert len(frontmatter.group(1)) <= 1024
    assert "MASP" in description or "melhoria" in description.lower()


def test_skill_and_reference_cover_the_eight_phases_and_closed_states():
    text = SKILL.read_text(encoding="utf-8") + REFERENCE.read_text(encoding="utf-8")
    routing = load_routing(ROUTING)
    assert all(phase["name"] in text for phase in routing["phases"])
    for state in ("PENDING", "IN_PROGRESS", "PASS", "FAIL", "BLOCKED", "NOT_RUN"):
        assert f"`{state}`" in text


def test_skill_documents_official_cli_commands_and_their_real_entry_point():
    text = SKILL.read_text(encoding="utf-8") + REFERENCE.read_text(encoding="utf-8")
    cli = (ROOT / "src" / "masp_skill" / "cli.py").read_text(encoding="utf-8")
    for command in ("validate-routing", "new-case", "transition", "case-revision", "validate-case"):
        assert command in cli
        assert f"masp_skill.cli {command}" in text


def test_skill_references_confirmed_superpowers_skills_and_no_required_rea():
    text = SKILL.read_text(encoding="utf-8") + REFERENCE.read_text(encoding="utf-8")
    matrix = tomllib.loads(ROUTING.read_text(encoding="utf-8"))
    declared = {
        item["name"]: Path(item["path"])
        for phase in matrix["phases"]
        for item in phase.get("skills", [])
        if item["name"].startswith("superpowers:")
    }
    required = {
        "superpowers:dispatching-parallel-agents": Path(
            r"C:\Users\marci\.codex\plugins\cache\openai-curated-remote\superpowers\7.0.1\skills\dispatching-parallel-agents\SKILL.md"
        ),
        "superpowers:subagent-driven-development": Path(
            r"C:\Users\marci\.codex\plugins\cache\openai-curated-remote\superpowers\7.0.1\skills\subagent-driven-development\SKILL.md"
        ),
    }
    assert all(path.is_file() for path in declared.values())
    assert all(path.is_file() for path in required.values())
    for name in (*declared, *required):
        assert name in text
    assert "REA" in text and "not" in text.lower() and "unavailable" in text.lower()
