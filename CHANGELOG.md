# Changelog — BulaLivre

Formato: `MAIOR.MENOR.CORRECAO`. A versão também aparece na tela principal do app
(`APP_VERSION` em `index.html`). Regras em `CLAUDE.md`. Entradas mais novas no topo.

## v1.0.0 — 2026-11-25

Primeira versão numerada. Reúne as melhorias de dados e da calculadora:

- **Número de versão** na tela principal (hero) e no rodapé.
- **Preenchimento do princípio ativo faltante** pelo nome do produto (`backfill_pa`
  em `build/update_data.py`): a ANVISA deixa ~20% dos registros sem princípio ativo;
  2.476 produtos passaram a ser identificados (248 deles associações multi-PA),
  incluindo tolerância à grafia z/s e proteção contra cátions minerais ambíguos.
  Isso reativou resumo + calculadora para produtos como o Ondansetron.
- **Memória da dose no aparelho** (localStorage): a posologia que o profissional
  ajusta fica salva só no dispositivo e é reposta na próxima visita. Nunca salva
  dados do paciente.
- **Canal de contribuição de dose** para revisão (botão na página do medicamento e no
  cálculo manual), configurável para Google Form ou issue do GitHub.
- Service worker: cache atualizado para `bulalivre-v13`.

### Antes da numeração (histórico resumido por commits)
- Calculadora em passos guiados e mais segurança.
- Calculadora acessível para todos os produtos; filtro por laboratório.
- Botão para ver/baixar a bula no Bulário da ANVISA.
- Dinâmica e cinética; cálculo manual; busca por sintomas.
