# Prompt de início de um caso MASP

Use este prompt depois de abrir o workspace isolado que receberá a investigação. Substitua os valores entre colchetes por caminhos e identificadores reais; confirme os limites do workspace antes de qualquer escrita.

```text
Conduza o caso [ID MASP] pelo fluxo de oito fases descrito em docs/masp/MASP-ARQUITETURA.md e na skill local skills/masp/SKILL.md.

Workspace de trabalho: [CAMINHO DO WORKSPACE ISOLADO]
Projeto/fonte em modo somente leitura: [CAMINHO DA FONTE, SE APLICÁVEL]
Problema relatado: [RELATO]
Critério de sucesso: [CRITÉRIO OBSERVÁVEL]
Limites autorizados: [ARQUIVOS, COMANDOS E OPERAÇÕES]

Antes de trabalhar:
1. Leia o AGENTS.md efetivo do workspace e confirme as ferramentas realmente disponíveis nesta sessão.
2. Leia a matriz docs/masp/masp-routing.toml e os contratos dos papéis pertinentes.
3. Rode `python -m masp_skill.cli validate-routing --routing docs/masp/masp-routing.toml --classification STATIC`.
4. Crie o manifesto sem sobrescrever nada: `python -m masp_skill.cli new-case --id [ID MASP] --output [ARQUIVO NOVO DENTRO DO WORKSPACE] --root [WORKSPACE]`.
5. Registre a revisão com `python -m masp_skill.cli case-revision --case [MANIFESTO]` e confira o manifesto com `python -m masp_skill.cli validate-case --case [MANIFESTO] --root [WORKSPACE]`.

Siga Identificação, Observação, Análise, Plano de ação, Ação, Verificação, Padronização e Conclusão na ordem. Não avance um gate sem suas evidências. Mantenha cada evidência dentro do workspace autorizado. Antes de cada transição, consulte a revisão atual e passe o SHA-256 esperado conforme `python -m masp_skill.cli transition --help`.

Classifique cada resultado como STATIC, SIMULATED ou RUNTIME e registre comando, saída, código de saída e limitações apropriados. STATIC e SIMULATED não provam comportamento real. Registre indisponibilidade de modelo, ferramenta, skill ou agente como BLOCKED; não faça fallback sem aprovação humana. Use NOT_RUN quando a verificação não foi executada.

Somente o coordenador delega. Filhos não criam subagentes; não permita escritores concorrentes no mesmo arquivo. Plano de ação exige aprovação humana antes da Ação; executor não aprova seu próprio trabalho. Alto risco exige parecer independente de Astra; se Astra não estiver disponível, bloqueie. Não altere arquivos fora dos limites aprovados, não acesse serviços/dados reais e não publique.

Ao concluir, valide o manifesto e entregue os resultados, evidências, riscos e pendências. Não encerre como PASS enquanto houver bloqueio relevante.
```

## Comandos da CLI

A CLI oferece `validate-routing`, `new-case`, `transition`, `case-revision` e `validate-case`. Consulte os argumentos da operação antes de usá-la: `python -m masp_skill.cli [comando] --help`. Os rótulos de ator, aprovação e modelo registrados pelo motor local são declarativos; não constituem autenticação.

## Situação da integração Codex

A configuração e os arquivos locais podem ser verificados estaticamente, mas a evidência runtime atual registra `BLOCKED` no carregamento estruturado da skill e na descoberta/delegação dos agentes. Consulte [`evidencias/codex-smoke.md`](evidencias/codex-smoke.md) e não declare esses recursos operacionais até obter evidência correlacionada da sessão real.
