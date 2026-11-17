# MASP — Ação Universal v2 (M05)

**Missão:** documentar as contramedidas realmente executadas, autorizadas externamente e limitadas ao escopo do Plano M04. Aplicável a indústria, serviços, tecnologia, logística, saúde, educação, meio ambiente, administração e cotidiano. **Execução documentada ≠ eficácia comprovada.**

## Pré-execução
Verificar M01 escopo/critério, M02 baseline, M03 causa/limitações, plano M04 e versão, riscos, limites, critérios de verificação e aprovação humana por canal competente. Campo `approval.status=approved`, hash ou nome em JSON **não autentica autorização**. Exigir isolamento/ambiente controlado, competência e condições de parada; se não comprovados, `BLOCKED`.

## Execução e handoff
Por tarefa registrar ID, plano, responsável, estado `performed|partial|failed|blocked|not_run`, procedimento ou comando realmente realizado, condição anterior/posterior, evidência e proveniência, testes imediatos, desvios, riscos novos e rollback/contingência realmente aplicados ou `NOT_RUN`. Não simular comando shell para atividade física/administrativa, nem chamar contingência de rollback integral. A fase 05 não demonstra eficácia: entregar registros, baseline, critérios, falhas e riscos à Verificação independente M06.

## Gate 05
Preservar exatamente `changes`, `diff`, `commands`, `results`, `no_self_approval`. Em situação não digital, `diff` é comparação descritiva de estado e `commands` representa procedimentos documentados ou inaplicabilidade fundamentada, não comando inventado.

**PASS:** execução e condições observadas suficientes para auditoria posterior, com aprovação real verificada fora da CLI. **FAIL:** ação/checagem realizada contraria critério. **BLOCKED:** requisito de autorização, segurança ou evidência essencial ausente. **NOT_RUN:** intervenção não realizada, não equivale a sucesso.

## Sidecar
`python -m masp_skill.cli validate-action-execution --record .tmp/acao.json --root .` confere apenas estrutura `STATIC`: IDs, estado, escopo, versão, segregação nominal e referências declaradas. Não executa intervenções, não confirma identidades ou fatos e não concede PASS ao Gate 05.

Restrições OTServer (checkout somente leitura, VPS, bancos, EXE desconhecido) aplicam-se **somente** quando o caso for OTServer. Procedimentos clínicos, industriais e de segurança exigem autoridade profissional competente.
