from copy import deepcopy
from pathlib import Path
import json

import pytest

from masp_skill.case import create_case, transition_case, validate_case
from masp_skill.evidence import make_evidence, validate_evidence
from masp_skill.routing import load_routing

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / 'docs' / 'masp' / 'masp-routing.toml'
ROUTING = load_routing(MATRIX)


def evidence(tmp_path, name='proof.txt', classification='SIMULATED', **kwargs):
    target = tmp_path / name
    target.write_text('observed result\n', encoding='utf-8')
    return make_evidence(target, ROOT, classification=classification, description='Recorded evidence', **kwargs)


def test_case_happy_path_records_hash_chained_events_and_validates(tmp_path):
    case = create_case('MASP-001', ROUTING)
    assert case['classification'] == 'SIMULATED'
    assert case['current_phase'] == 'Identificação'
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path)], ROUTING)
    case = transition_case(case, 'PASS', 'masp-coordenador', [evidence(tmp_path, 'proof2.txt')], ROUTING)
    assert case['ledger'][1]['previous_hash'] == case['ledger'][0]['event_hash']
    assert validate_case(case, ROUTING, ROOT) == []


def test_passed_phase_can_start_only_its_next_phase(tmp_path):
    case = create_case('MASP-PHASES', ROUTING)
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'phase-start.txt')], ROUTING)
    case = transition_case(case, 'PASS', 'masp-coordenador', [evidence(tmp_path, 'phase-pass.txt')], ROUTING)
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'next-phase.txt')], ROUTING, phase='Observação')
    assert case['current_phase'] == 'Observação'
    assert validate_case(case, ROUTING, ROOT) == []


def test_rejects_phase_skip_and_pass_without_usable_evidence(tmp_path):
    case = create_case('MASP-002', ROUTING)
    with pytest.raises(ValueError, match='phase|fase'):
        transition_case(case, 'PASS', 'masp-coordenador', [evidence(tmp_path)], ROUTING, phase='Análise')
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'start.txt')], ROUTING)
    with pytest.raises(ValueError, match='evidence|evidência'):
        transition_case(case, 'PASS', 'masp-coordenador', [], ROUTING)


def test_executor_cannot_approve_own_action(tmp_path):
    case = create_case('MASP-003', ROUTING)
    case['current_phase'] = 'Ação'
    with pytest.raises(ValueError, match='executor|auto|coordinator'):
        transition_case(case, 'PASS', 'masp-executor', [evidence(tmp_path)], ROUTING)


def test_action_requires_human_approved_plan(tmp_path):
    case = create_case('MASP-004', ROUTING)
    case['current_phase'] = 'Ação'
    with pytest.raises(ValueError, match='human|humana|approval|aprova'):
        transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path)], ROUTING)
    case['approvals'] = {'plan': {'approved_by': 'user', 'evidence_id': 'approval-1'}}
    ev = evidence(tmp_path, 'plan-approval.txt', evidence_id='approval-1')
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [ev], ROUTING)
    assert case['state'] == 'IN_PROGRESS'


def test_blocked_stops_forward_progress_but_fail_can_return_to_declared_phase(tmp_path):
    case = create_case('MASP-005', ROUTING)
    case = transition_case(case, 'BLOCKED', 'masp-coordenador', [evidence(tmp_path)], ROUTING)
    with pytest.raises(ValueError, match='BLOCKED|blocked|bloquead'):
        transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'later.txt')], ROUTING)
    case = create_case('MASP-006', ROUTING)
    case['current_phase'] = 'Análise'
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'analysis.txt')], ROUTING)
    case = transition_case(case, 'FAIL', 'masp-coordenador', [evidence(tmp_path, 'fail.txt')], ROUTING)
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'return.txt')], ROUTING, phase='Observação')
    assert case['current_phase'] == 'Observação'


def test_not_run_or_static_evidence_cannot_satisfy_runtime_gate(tmp_path):
    case = create_case('MASP-007', ROUTING)
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'start.txt')], ROUTING)
    ev = evidence(tmp_path, classification='STATIC')
    with pytest.raises(ValueError, match='RUNTIME|runtime'):
        transition_case(case, 'PASS', 'masp-coordenador', [ev], ROUTING, required_classification='RUNTIME')
    assert validate_evidence([{**ev, 'path': 'missing.txt'}], ROOT)


def test_manual_ledger_tampering_and_non_coordinator_actor_are_rejected(tmp_path):
    case = create_case('MASP-008', ROUTING)
    with pytest.raises(ValueError, match='coordinator|coordenador|actor|ator'):
        transition_case(case, 'IN_PROGRESS', 'masp-observador', [evidence(tmp_path)], ROUTING)
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path)], ROUTING)
    case['ledger'][0]['actor'] = 'tampered'
    assert any('hash' in error.lower() or 'integrity' in error.lower() for error in validate_case(case, ROUTING, ROOT))


def test_unavailable_model_blocks_case_without_fallback(tmp_path):
    routing = deepcopy(ROUTING)
    routing['roles']['masp-identificador']['available'] = False
    case = create_case('MASP-009', routing)
    assert case['state'] == 'BLOCKED'
    with pytest.raises(ValueError, match='BLOCKED|blocked'):
        transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path)], routing)


def test_high_risk_requires_astra_opinion_before_pass(tmp_path):
    case = create_case('MASP-010', ROUTING, high_risk=True)
    case = transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'start.txt')], ROUTING)
    with pytest.raises(ValueError, match='Astra|astra|audit|auditoria'):
        transition_case(case, 'PASS', 'masp-coordenador', [evidence(tmp_path)], ROUTING)
    astra = evidence(tmp_path, 'astra.txt', role='masp-especialista-critico', opinion='PASS')
    case = transition_case(case, 'PASS', 'masp-coordenador', [evidence(tmp_path, 'proof.txt'), astra], ROUTING)
    assert case['state'] == 'PASS'


def test_parallel_tasks_with_overlapping_write_paths_are_rejected():
    from masp_skill.case import validate_parallel_tasks
    tasks = [{'id': 'a', 'writes': ['src/a.py']}, {'id': 'b', 'writes': ['src/a.py']}]
    assert any('write' in error.lower() or 'escrita' in error.lower() for error in validate_parallel_tasks(tasks, ROUTING))


def test_fixture_manifest_is_valid():
    fixture = ROOT / 'tests' / 'fixtures' / 'cases' / 'valid-case.json'
    case = json.loads(fixture.read_text(encoding='utf-8'))
    assert validate_case(case, ROUTING, ROOT) == []
