from copy import deepcopy
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import pytest

from masp_skill.case import GATE_REQUIREMENTS, _event_hash, case_revision, create_case, transition_case, validate_case, validate_parallel_tasks
from masp_skill.cli import main
from masp_skill.evidence import make_evidence, validate_evidence
from masp_skill.routing import load_routing

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / 'docs' / 'masp' / 'masp-routing.toml'
ROUTING = load_routing(MATRIX)
ALL_CRITERIA = sorted({criterion for requirements in GATE_REQUIREMENTS.values() for criterion in requirements})


def evidence(tmp_path, name='proof.txt', classification='SIMULATED', **metadata):
    target = tmp_path / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('observed result\n', encoding='utf-8')
    properties = {
        'satisfies': ALL_CRITERIA,
        'command': 'python -m pytest',
        'exit_code': 0,
        'stdout': 'ok',
        'stderr': '',
        **metadata,
    }
    return make_evidence(target, tmp_path, classification=classification, description='Recorded evidence', **properties)


def start(case, tmp_path, routing=ROUTING, phase=None, **record):
    name = phase or case['current_phase']
    return transition_case(
        case, 'IN_PROGRESS', 'masp-coordenador',
        [evidence(tmp_path, f'{name}-start.json', **record)], routing, phase=phase, root=tmp_path,
    )


def pass_gate(case, tmp_path, routing=ROUTING, phase=None, **record):
    name = phase or case['current_phase']
    return transition_case(
        case, 'PASS', 'masp-coordenador',
        [evidence(tmp_path, f'{name}-pass.json', **record)], routing, phase=phase, root=tmp_path,
    )


def move_to_phase(case, target, tmp_path, routing=ROUTING):
    names = [item['name'] for item in routing['phases']]
    while case['current_phase'] != target:
        current = case['current_phase']
        if case['state'] == 'PENDING':
            case = start(case, tmp_path, routing)
        if current == 'Plano de ação':
            case = pass_gate(case, tmp_path, routing, approval_type='human_plan', approved_by='operator-label')
        else:
            case = pass_gate(case, tmp_path, routing)
        next_phase = names[names.index(current) + 1]
        case = start(case, tmp_path, routing, phase=next_phase)
    return case


def test_case_happy_path_records_hash_chained_events_and_validates(tmp_path):
    case = create_case('MASP-001', ROUTING)
    assert case['classification'] == 'SIMULATED'
    assert case['current_phase'] == 'Identificação'
    case = start(case, tmp_path)
    case = pass_gate(case, tmp_path)
    assert case['ledger'][1]['previous_hash'] == case['ledger'][0]['event_hash']
    assert validate_case(case, ROUTING, tmp_path) == []


def test_only_next_phase_after_pass_and_declared_return_after_fail_are_valid(tmp_path):
    case = pass_gate(start(create_case('MASP-NEXT', ROUTING), tmp_path), tmp_path)
    case = start(case, tmp_path, phase='Observação')
    assert case['current_phase'] == 'Observação'
    case = move_to_phase(create_case('MASP-RETURN', ROUTING), 'Análise', tmp_path)
    case = transition_case(case, 'FAIL', 'masp-coordenador', [evidence(tmp_path, 'analysis-fail.json')], ROUTING, root=tmp_path)
    case = start(case, tmp_path, phase='Observação')
    assert case['current_phase'] == 'Observação'
    with pytest.raises(ValueError, match='phase|fase'):
        transition_case(case, 'IN_PROGRESS', 'masp-coordenador', [evidence(tmp_path, 'skip.json')], ROUTING, phase='Conclusão', root=tmp_path)


@pytest.mark.parametrize('target_state', ['BLOCKED', 'NOT_RUN'])
def test_replay_accepts_declared_fail_return_ending_in_blocked_or_not_run(tmp_path, target_state):
    case = move_to_phase(create_case(f'MASP-RETURN-{target_state}', ROUTING), 'Análise', tmp_path)
    case = transition_case(case, 'FAIL', 'masp-coordenador', [evidence(tmp_path, f'{target_state}-failure.json')], ROUTING, root=tmp_path)
    case = transition_case(case, target_state, 'masp-coordenador', [evidence(tmp_path, f'{target_state}-return.json')], ROUTING, phase='Observação', root=tmp_path)
    assert validate_case(case, ROUTING, tmp_path) == []


def test_pass_without_evidence_and_missing_gate_criteria_are_rejected(tmp_path):
    case = start(create_case('MASP-NO-EVIDENCE', ROUTING), tmp_path)
    with pytest.raises(ValueError, match='evidence|evidência'):
        transition_case(case, 'PASS', 'masp-coordenador', [], ROUTING, root=tmp_path)
    proof = evidence(tmp_path)
    proof['satisfies'] = ['problem']
    with pytest.raises(ValueError, match='gate|criteria|critério'):
        transition_case(case, 'PASS', 'masp-coordenador', [proof], ROUTING, root=tmp_path)


def test_phase_origin_and_high_risk_metadata_are_committed_and_replay_is_required(tmp_path):
    case = pass_gate(start(create_case('MASP-REPLAY', ROUTING, high_risk=True), tmp_path), tmp_path)
    edited = deepcopy(case)
    edited['high_risk'] = False
    assert any('genesis' in error.lower() or 'origin' in error.lower() for error in validate_case(edited, ROUTING, tmp_path))
    edited = deepcopy(case)
    edited['current_phase'] = 'Análise'
    assert validate_case(edited, ROUTING, tmp_path)
    edited = deepcopy(case)
    edited['ledger'].reverse()
    previous = '0' * 64
    for index, event in enumerate(edited['ledger'], start=1):
        event['sequence'] = index
        event['previous_hash'] = previous
        event['event_hash'] = _event_hash(event)
        previous = event['event_hash']
    assert any('replay' in error.lower() or 'phase' in error.lower() for error in validate_case(edited, ROUTING, tmp_path))


def test_replay_rejects_transition_with_empty_evidence_even_if_event_hash_is_recomputed(tmp_path):
    case = start(create_case('MASP-EMPTY-REPLAY', ROUTING), tmp_path)
    case['ledger'][0]['evidence'] = []
    case['ledger'][0]['event_hash'] = _event_hash(case['ledger'][0])
    assert any('evidence' in error.lower() or 'evidência' in error.lower() for error in validate_case(case, ROUTING, tmp_path))


def test_plan_gate_requires_a_simulated_human_approval_record(tmp_path):
    case = move_to_phase(create_case('MASP-PLAN', ROUTING), 'Plano de ação', tmp_path)
    with pytest.raises(ValueError, match='approval|aprova'):
        pass_gate(case, tmp_path)
    case = pass_gate(case, tmp_path, approval_type='human_plan', approved_by='operator-label')
    case = start(case, tmp_path, phase='Ação')
    assert case['state'] == 'IN_PROGRESS'


def test_executor_is_not_accepted_as_coordinator_label(tmp_path):
    case = create_case('MASP-ACTOR', ROUTING)
    with pytest.raises(ValueError, match='simulation|simulação|coordinator|coordenador'):
        transition_case(case, 'IN_PROGRESS', 'masp-executor', [evidence(tmp_path)], ROUTING, root=tmp_path)


def test_blocked_case_does_not_advance_and_unavailable_phase_model_blocks_start(tmp_path):
    routing = deepcopy(ROUTING)
    routing['roles']['masp-identificador']['available'] = False
    case = create_case('MASP-MODEL', routing)
    assert case['state'] == 'BLOCKED'
    with pytest.raises(ValueError, match='BLOCKED|blocked'):
        start(case, tmp_path, routing)
    blocked = transition_case(create_case('MASP-BLOCK', ROUTING), 'BLOCKED', 'masp-coordenador', [evidence(tmp_path)], ROUTING, root=tmp_path)
    with pytest.raises(ValueError, match='BLOCKED|blocked'):
        start(blocked, tmp_path)


def test_runtime_verification_requires_command_exit_and_result(tmp_path):
    case = move_to_phase(create_case('MASP-VERIFY', ROUTING), 'Verificação', tmp_path)
    incomplete = evidence(tmp_path, classification='RUNTIME', command='', exit_code=None, stdout='', stderr='')
    with pytest.raises(ValueError, match='command|exit|result|resultado'):
        pass_gate(case, tmp_path, classification='RUNTIME', command='', exit_code=None, stdout='', stderr='')
    proof = evidence(tmp_path, classification='STATIC')
    with pytest.raises(ValueError, match='RUNTIME|runtime'):
        transition_case(case, 'PASS', 'masp-coordenador', [proof], ROUTING, root=tmp_path)
    assert incomplete


def test_high_risk_verification_requires_a_reported_astra_runtime_opinion_and_available_model(tmp_path):
    case = move_to_phase(create_case('MASP-ASTRA', ROUTING, high_risk=True), 'Verificação', tmp_path)
    with pytest.raises(ValueError, match='Astra|astra|audit|auditoria'):
        pass_gate(case, tmp_path, classification='RUNTIME')
    astra = evidence(tmp_path, 'astra.json', classification='RUNTIME', role='masp-especialista-critico', model='gpt-6-astra', effort='medium', opinion='PASS')
    case = transition_case(case, 'PASS', 'masp-coordenador', [astra], ROUTING, root=tmp_path)
    assert case['state'] == 'PASS'
    with pytest.raises(ValueError, match='Astra|astra|effort|esforço'):
        pass_gate(move_to_phase(create_case('MASP-ASTRA-EFFORT', ROUTING, high_risk=True), 'Verificação', tmp_path), tmp_path, classification='RUNTIME', role='masp-especialista-critico', model='gpt-6-astra', effort='high', opinion='PASS')
    bad_routing = deepcopy(ROUTING)
    bad_routing['roles']['masp-especialista-critico']['model'] = 'gpt-6.1-sol'
    with pytest.raises(ValueError, match='Astra|astra|model|modelo'):
        move_to_phase(create_case('MASP-ASTRA-MATRIX', bad_routing, high_risk=True), 'Verificação', tmp_path, bad_routing)
    unavailable = deepcopy(ROUTING)
    unavailable['roles']['masp-especialista-critico']['available'] = False
    with pytest.raises(ValueError, match='Astra|astra|model|modelo|BLOCKED'):
        move_to_phase(create_case('MASP-ASTRA-UNAVAILABLE', unavailable, high_risk=True), 'Verificação', tmp_path, unavailable)


def test_evidence_paths_must_resolve_inside_root_and_exist(tmp_path):
    outside = tmp_path.parent / 'outside-evidence.txt'
    outside.write_text('not in root', encoding='utf-8')
    assert any('outside' in issue.lower() or 'root' in issue.lower() for issue in validate_evidence([
        {'id': 'escape', 'path': '../outside-evidence.txt', 'classification': 'RUNTIME', 'description': 'escape'}
    ], tmp_path))
    assert any('missing file' in issue.lower() for issue in validate_evidence([
        {'id': 'missing', 'path': 'missing.txt', 'classification': 'SIMULATED', 'description': 'missing'}
    ], tmp_path))


def test_ledger_tampering_is_rejected_and_simulated_role_claims_are_not_authenticated(tmp_path):
    case = start(create_case('MASP-TAMPER', ROUTING), tmp_path)
    case['ledger'][0]['actor'] = 'masp-executor'
    assert validate_case(case, ROUTING, tmp_path)
    assert case['classification'] == 'SIMULATED'


def test_parallel_tasks_enforce_effective_limit_normalized_paths_and_root(tmp_path):
    tasks = [{'id': 'a', 'writes': ['src/a.py']}, {'id': 'b', 'writes': ['src/./a.py']}]
    assert any('write' in issue.lower() for issue in validate_parallel_tasks(tasks, ROUTING, root=tmp_path))
    too_many = [{'id': str(i), 'writes': [f'file-{i}.txt']} for i in range(4)]
    assert any('limit' in issue.lower() for issue in validate_parallel_tasks(too_many, ROUTING, root=tmp_path, effective_limit=2))
    escaping = [{'id': 'escape', 'writes': ['../outside.py']}]
    assert any('root' in issue.lower() or 'outside' in issue.lower() for issue in validate_parallel_tasks(escaping, ROUTING, root=tmp_path))


def test_fixture_manifest_is_valid():
    fixture = ROOT / 'tests' / 'fixtures' / 'cases' / 'valid-case.json'
    case = json.loads(fixture.read_text(encoding='utf-8'))
    assert validate_case(case, ROUTING, ROOT) == []


def test_cli_concurrent_transitions_use_lock_and_compare_and_swap_revision(tmp_path, capsys):
    case_path = tmp_path / 'case.json'
    case_path.write_text(json.dumps(create_case('MASP-CAS', ROUTING), ensure_ascii=False), encoding='utf-8')
    proof = evidence(tmp_path, 'transition-proof.json')
    evidence_path = tmp_path / 'evidence.json'
    evidence_path.write_text(json.dumps([proof], ensure_ascii=False), encoding='utf-8')
    revision = case_revision(case_path.read_bytes())
    command = [
        'transition', '--case', str(case_path), '--state', 'IN_PROGRESS',
        '--actor', 'masp-coordenador', '--evidence', str(evidence_path),
        '--routing', str(MATRIX), '--root', str(tmp_path), '--expected-revision', revision,
    ]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(main, (command, command)))
    assert sorted(results) == [0, 1]
    capsys.readouterr()
    updated = case_path.read_bytes()
    assert case_revision(updated) != revision
    assert validate_case(json.loads(updated), ROUTING, tmp_path) == []
    assert case_path.with_name('case.json.lock').is_file()


def test_cli_new_case_normalizes_output_under_root_and_refuses_escape_or_overwrite(tmp_path, capsys):
    assert main(['new-case', '--id', 'MASP-NEW', '--output', 'cases/new.json', '--root', str(tmp_path), '--routing', str(MATRIX)]) == 0
    capsys.readouterr()
    target = tmp_path / 'cases' / 'new.json'
    assert target.is_file()
    assert main(['new-case', '--id', 'MASP-ESCAPE', '--output', '../escape.json', '--root', str(tmp_path), '--routing', str(MATRIX)]) == 1
    capsys.readouterr()
    assert main(['new-case', '--id', 'MASP-NEW', '--output', 'cases/new.json', '--root', str(tmp_path), '--routing', str(MATRIX)]) == 1
    assert json.loads(target.read_text(encoding='utf-8'))['case_id'] == 'MASP-NEW'


def test_case_revision_works_without_routing_file_in_current_directory(tmp_path, monkeypatch, capsys):
    target = tmp_path / 'case.json'
    target.write_bytes(b'{"manifest": "not loaded by revision command"}')
    monkeypatch.chdir(tmp_path)
    assert main(['case-revision', '--case', str(target)]) == 0
    assert capsys.readouterr().out.strip() == f'SHA256: {case_revision(target.read_bytes())}'
