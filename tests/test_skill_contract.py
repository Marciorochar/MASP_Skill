from pathlib import Path
import os
import re
import tomllib

import pytest

from masp_skill.routing import load_routing


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "masp" / "SKILL.md"
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


def _superpowers_roots():
    """Find optional external Superpowers installs without assuming a host path."""
    configured = os.environ.get("MASP_SUPERPOWERS_SKILLS_DIR")
    if configured:
        yield Path(configured).expanduser()
    homes = {Path.home()}
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        homes.add(Path(user_profile).expanduser())
    for home in homes:
        cache = home / ".codex" / "plugins" / "cache" / "openai-curated-remote" / "superpowers"
        if cache.is_dir():
            yield from cache.glob("*/skills")


def test_skill_references_declared_superpowers_skills_and_no_required_rea():
    text = SKILL.read_text(encoding="utf-8") + REFERENCE.read_text(encoding="utf-8")
    matrix = tomllib.loads(ROUTING.read_text(encoding="utf-8"))
    declared = [
        item
        for phase in matrix["phases"]
        for item in phase.get("skills", [])
        if item["name"].startswith("superpowers:")
    ]
    assert declared
    for item in declared:
        assert item["name"] in text
        assert item["path"].endswith("/SKILL.md")
    # Optional external integration is reported as skipped when unavailable.
    roots = [root for root in _superpowers_roots() if root.is_dir()]
    if not roots:
        pytest.skip("Superpowers skill files are optional; install or set MASP_SUPERPOWERS_SKILLS_DIR to validate their availability")
    for item in declared:
        skill_name = item["name"].partition(":")[2]
        if item.get("required", True):
            assert any((root / skill_name / "SKILL.md").is_file() for root in roots), skill_name
    assert "REA" in text and "not" in text.lower() and "unavailable" in text.lower()
