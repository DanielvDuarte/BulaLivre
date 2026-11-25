# BulaLivre — instruções para o Claude

App estático (roda no GitHub Pages a partir da branch `main`) de consulta de
medicamentos da ANVISA, com calculadora de dose para profissionais.

## ⚠️ REGRA DE VERSÃO (ler SEMPRE antes de alterar)

**Toda alteração no app DEVE subir o número de versão.** Sem exceção.

A cada mudança, nesta ordem:

1. **`index.html`** → incremente a constante `APP_VERSION` (perto do topo, logo após
   `OFFLINE`). É ela que aparece na tela principal (hero) e no rodapé.
2. **`sw.js`** → se a mudança tocou `index.html` ou o "app shell" (ícones, manifest),
   incremente também o `VERSION` do cache (ex.: `bulalivre-v13` → `bulalivre-v14`).
   Sem isso, quem instalou o app (PWA) continua recebendo a versão antiga do cache.
3. **`CHANGELOG.md`** → adicione uma entrada no topo com a nova versão, a data e o que
   mudou (uma linha por item).

### Como escolher o número (semver simplificado `MAIOR.MENOR.CORRECAO`)
- **CORREÇÃO** (`1.0.0` → `1.0.1`): correção de bug, ajuste de texto, refino pequeno.
- **MENOR** (`1.0.1` → `1.1.0`): recurso novo que não quebra o que existia.
- **MAIOR** (`1.x` → `2.0.0`): mudança grande/incompatível (ex.: novo formato do
  `bulas.json`, reestruturação da calculadora).

> Se o usuário pedir uma alteração e esquecer de mencionar a versão, **suba mesmo
> assim** e avise no final qual virou a nova versão. Esta é a convenção combinada.

## Estrutura

| Arquivo | O quê |
|---|---|
| `index.html` | O app inteiro (HTML+CSS+JS num arquivo). Contém `APP_VERSION`, a lista curada de doses (`DOSES`), resumos (`info_substancias` embutido via `bulas.json`), a calculadora e as views. |
| `bulas.json` | Base de produtos. Gerada por `build/update_data.py` a partir dos Dados Abertos da ANVISA. **Não editar à mão** (é sobrescrita no build). |
| `build/update_data.py` | Baixa a ANVISA, gera `bulas.json` e preenche o princípio ativo faltante pelo nome (`backfill_pa`). |
| `sw.js` | Service worker (cache offline). Tem `VERSION` próprio do cache. |
| `CHANGELOG.md` | Histórico de versões. |

## Regras de segurança (app médico — não afrouxar)

- **Dose nunca entra na calculadora sem validação profissional.** A lista `DOSES` é
  curada à mão; doses sugeridas por usuários passam pelo canal de contribuição
  (`sugerirDoseUrl`) e só entram depois de revisadas.
- **Nunca salvar dados do paciente.** A "memória da dose" (localStorage,
  `bl_doses_prof`) guarda só posologia/apresentação ajustada pelo profissional.
- **Preenchimento de princípio ativo (`backfill_pa`)** só IDENTIFICA a molécula pelo
  nome; associações viram multi-PA (nunca caem na calculadora de dose única); cátions
  minerais ambíguos (sódio, cálcio, ferro...) não servem de chave.
- Não implementar "baixar dose online automática": não há fonte estruturada confiável
  e é risco ao paciente.

## Fluxo de deploy

Branch de desenvolvimento: `claude/cool-carson-0ctgyy`. Ao finalizar, o usuário
autoriza levar para `main` (commit + push). O GitHub Pages republica em ~1–2 min; no
app, o botão **↻ Atualizar** força o recarregamento do `bulas.json`.

## Teste rápido (navegador)

```bash
python3 -m http.server 8099   # servir a pasta
# abrir http://localhost:8099/index.html e checar busca, página do remédio e calculadora
```
Chromium + Playwright estão disponíveis para testes headless (`chromium.launch({args:['--no-sandbox']})`).
