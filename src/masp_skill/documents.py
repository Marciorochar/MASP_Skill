"""Static structure check of Markdown evidence documents against MASP gate criteria.

A document passes for a criterion when it has a heading, a bold label or a
``label:`` line named like that criterion (Portuguese or English alias, or the
criterion id itself, e.g. `hypotheses`) whose body is not empty or a
placeholder. This proves structure only: it does not prove the text is true,
sufficient, written by anyone in particular, or that a gate passed.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

# Criteria that depend on records other than a document (approval metadata).
EXEMPT = frozenset({"human_approval", "no_self_approval"})

_RAW_ALIASES: dict[str, tuple[str, ...]] = {
    "problem": ("Problema", "Declaração do problema", "Problem", "Problem statement"),
    "impact": ("Impacto", "Impact"),
    "scope": ("Escopo", "Scope"),
    "exclusions": ("Exclusões", "Fora do escopo", "Escopo e exclusões", "Exclusions", "Out of scope", "Scope and exclusions"),
    "success_metric": ("Métrica de sucesso", "Critério de sucesso", "Success metric", "Success criteria"),
    "baseline": ("Baseline", "Linha de base"),
    "environment": ("Ambiente", "Environment"),
    "collection_method": ("Método de coleta", "Coleta", "Collection method"),
    "reproducible_result_or_limitation": (
        "Resultado reproduzível", "Limitações", "Limitação", "Reproducible result", "Limitations"),
    "hypotheses": ("Hipóteses", "Hypotheses"),
    "evidence_for_and_against": (
        "Evidências a favor e contra", "Evidências", "Evidence for and against", "Evidence"),
    "root_cause_or_explicit_inconclusive": (
        "Causa raiz", "Causa raiz sustentada", "Inconclusão", "Root cause", "Inconclusive"),
    "tasks": ("Tarefas", "Tasks"),
    "owners": ("Responsáveis", "Owners"),
    "risks": ("Riscos", "Risks"),
    "rollback": ("Rollback", "Reversão"),
    "tests": ("Testes", "Critérios de teste", "Tests"),
    "changes": ("Mudanças", "Alterações", "Arquivos modificados", "Changes"),
    "diff": ("Diff", "Resumo do diff"),
    "commands": ("Comandos", "Commands"),
    "results": ("Resultados", "Results"),
    "baseline_comparison": ("Comparação com o baseline", "Comparação com baseline", "Baseline comparison"),
    "runtime_tests": ("Testes runtime", "Runtime tests"),
    "relevant_regressions": ("Regressões relevantes", "Regressões", "Regressions"),
    "independent_review": ("Revisão independente", "Independent review"),
    "preventive_control": ("Controle preventivo", "Preventive control"),
    "owner": ("Responsável", "Proprietário", "Owner"),
    "trigger": ("Gatilho", "Trigger"),
    "regression": ("Regressão", "Teste de regressão", "Regression"),
    "complete_ledger": ("Ledger", "Ledger completo", "Complete ledger"),
    "limitations": ("Limitações", "Limitations"),
    "residual_risks": ("Riscos residuais", "Residual risks"),
    "pending_items": ("Pendências", "Pending items"),
    "audit_opinion": ("Parecer de auditoria", "Parecer", "Audit opinion"),
}

MIN_WORDS = 2
MIN_ALNUM = 8
_PLACEHOLDER_WORDS = {
    "todo", "tbd", "definir", "a", "preencher", "na", "n", "xxx", "lorem", "ipsum", "descrever", "pendente",
}

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_LABEL_RE = re.compile(r"^(?P<indent>\s*)(?:[-*+]\s+|\d+[.)]\s+)?(?P<label>[^:\n]{1,80}?):(?P<rest>.*)$")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")


def _norm(text: str) -> str:
    text = text.replace("*", " ").replace("`", " ")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\([^)]*\)", " ", text)
    text = text.lower().replace("_", " ")
    text = re.sub(r"^\s*\d+(?:\.\d+)*[.)]?\s+", "", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


ALIASES: dict[str, tuple[str, ...]] = {
    criterion: tuple(sorted({_norm(alias) for alias in raw} | {_norm(criterion)}))
    for criterion, raw in _RAW_ALIASES.items()
}
_KNOWN_LABELS = frozenset(alias for values in ALIASES.values() for alias in values)


def _matches(label: str, aliases: Iterable[str]) -> bool:
    return any(label == alias or label.startswith(alias + " ") for alias in aliases)


def _is_known_label(label: str) -> bool:
    return _matches(label, _KNOWN_LABELS)


def documentable_criteria(criteria: Iterable[str]) -> list[str]:
    """Criteria this check can verify in a document (known and not exempt)."""
    return sorted({item for item in criteria if isinstance(item, str) and item in ALIASES and item not in EXEMPT})


def _parse(text: str) -> list[tuple]:
    """Return (kind, level_or_indent, normalized_label, rest, raw_line) per line."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    parsed: list[tuple] = []
    in_fence = False
    for line in text.splitlines():
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            parsed.append(("text", 0, "", line, line))
            continue
        if in_fence:
            parsed.append(("text", 0, "", line, line))
            continue
        heading = _HEADING_RE.match(line)
        if heading:
            parsed.append(("heading", len(heading.group(1)), _norm(heading.group(2)), "", line))
            continue
        label = _LABEL_RE.match(line)
        if label:
            indent = len(label.group("indent").expandtabs(4))
            parsed.append(("label", indent, _norm(label.group("label")), label.group("rest").replace("*", " "), line))
            continue
        parsed.append(("text", 0, "", line, line))
    return parsed


def _body(parsed: list[tuple], index: int) -> str:
    kind, level, _label, rest, _raw = parsed[index]
    pieces: list[str] = [] if kind == "heading" else [rest]
    for other in parsed[index + 1:]:
        other_kind, other_level, other_label = other[0], other[1], other[2]
        if kind == "heading":
            if other_kind == "heading" and other_level <= level:
                break
        else:
            if other_kind == "heading":
                break
            if other_kind == "label" and other_level <= level and _is_known_label(other_label):
                break
        pieces.append(other[4])
    return "\n".join(pieces)


def _meaningful(body: str) -> bool:
    body = re.sub(r"\[[^\]]*\](?!\()", " ", body)
    body = re.sub(r"^[\s|:\-]*$", " ", body, flags=re.M)
    words = re.findall(r"[^\W_]+", body)
    if len(words) < MIN_WORDS or sum(len(word) for word in words) < MIN_ALNUM:
        return False
    return not all(_norm(word) in _PLACEHOLDER_WORDS for word in words)


def check_markdown_criteria(text: str, criteria: Iterable[str]) -> list[str]:
    """Return one error per documentable criterion lacking a non-empty section."""
    parsed = _parse(text)
    errors: list[str] = []
    for criterion in documentable_criteria(criteria):
        aliases = ALIASES[criterion]
        found = False
        ok = False
        for index, entry in enumerate(parsed):
            if entry[0] == "text" or not _matches(entry[2], aliases):
                continue
            found = True
            if _meaningful(_body(parsed, index)):
                ok = True
                break
        if not found:
            names = ", ".join(_RAW_ALIASES[criterion][:3])
            errors.append(f"criterion {criterion!r}: no heading or label named like {names} (or `{criterion}`)")
        elif not ok:
            errors.append(f"criterion {criterion!r}: section is empty or only a placeholder")
    return errors
