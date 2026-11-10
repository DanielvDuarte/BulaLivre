# BulaLivre (offline + GitHub Pages)

Consulta de medicamentos **por sintoma** (ex.: "dor de cabeça") e por nome/princípio ativo/laboratório.
Roda como site estático no **GitHub Pages**, se atualiza sozinho a partir dos **Dados Abertos da ANVISA**
e tem um botão para **baixar uma cópia offline** (celular/computador).

> ⚕️ Material de **referência** — não substitui a bula nem a orientação de médico/farmacêutico.

## O que tem aqui

| Arquivo | Função |
|---|---|
| `index.html` | O app (busca, filtros, botões Atualizar e Baixar offline). |
| `bulas.json` | A base de dados. Já vem com uma base inicial curada; é **substituída** pela base completa da ANVISA quando a atualização roda. |
| `build/update_data.py` | Baixa o dataset da ANVISA e gera o `bulas.json`. |
| `build/mapa_sintomas.json` | Mapa *princípio ativo → sintomas*. É o que faz a busca por sintoma funcionar. **Edite para melhorar a busca.** |
| `.github/workflows/atualizar-dados.yml` | GitHub Action: atualiza a base (1 clique ou mensal). |

## Como funciona a atualização (importante)

O site é **estático** (Pages não tem servidor), e o portal da ANVISA não libera acesso direto pelo
navegador. Então quem baixa e processa os dados é o **GitHub Action** (os runners do GitHub têm internet):
ele roda o `update_data.py`, gera o `bulas.json` novo e faz commit. O botão **↻ Atualizar** no app
apenas **recarrega** esse `bulas.json` já publicado.

```
GitHub Action (mensal ou 1 clique)  ->  baixa ANVISA  ->  gera bulas.json  ->  commit
                                                                                   |
Você acessa o site (Pages)  <-------------------------------------------- Pages publica
      |
      +-- botão "Atualizar": recarrega o bulas.json mais recente
      +-- botão "Baixar offline": gera 1 HTML com a base embutida (funciona sem internet)
```

## Passo a passo — publicar no GitHub Pages

1. Crie um repositório no GitHub (ex.: `vademecum`) e envie **todos** estes arquivos para a branch `main`.
2. No repositório: **Settings → Pages**.
   - Em **Source**, escolha **Deploy from a branch**.
   - Branch: **main**, pasta **/ (root)** → **Save**.
3. Aguarde ~1 min. O site fica em:
   `https://SEU_USUARIO.github.io/vademecum/`
4. Primeira carga da base completa da ANVISA: vá na aba **Actions → "Atualizar base da ANVISA" → Run workflow**.
   Isso baixa os dados, gera o `bulas.json` completo e commita. Em seguida, clique **↻ Atualizar** no site.

> Depois disso, a base se atualiza sozinha todo dia 1º do mês (dá pra mudar o agendamento no arquivo do workflow).

## Rodar/gerar a base localmente (opcional)

Numa máquina com internet:

```bash
python build/update_data.py
# gera bulas.json na raiz do projeto
```

Se a URL ou o layout do dataset da ANVISA mudar:

```bash
python build/update_data.py --url "https://dados.anvisa.gov.br/dados/ARQUIVO.csv"
```

O script detecta as colunas automaticamente (nome, empresa/laboratório, princípio ativo, classe, tarja,
situação). Se precisar, ajuste as listas em `COLS`, dentro do `update_data.py`.

## Melhorar a busca por sintoma

A ANVISA fornece produto, laboratório, princípio ativo e classe — **não** o texto de "para que serve".
Por isso os sintomas são deduzidos do **princípio ativo** via `build/mapa_sintomas.json`:

```json
"paracetamol": ["dor de cabeça", "cefaleia", "febre", "dor"]
```

A chave é comparada (sem acento, minúscula) como parte do princípio ativo do produto. Todo produto cujo
ativo contenha essa chave herda esses sintomas. Para cobrir mais casos, é só adicionar entradas.
Produtos sem ativo mapeado continuam aparecendo na busca por **nome / laboratório / princípio ativo**.

## Uso offline

### Opção 1 — Instalar como app (recomendado no celular)

O BulaLivre é um **PWA**: depois de abrir o site uma vez, dá para instalá-lo como ícone de app, e ele
passa a funcionar **sem internet** (um *service worker* guarda o app e a base em cache).

- **iPhone/iPad (Safari):** toque em **Compartilhar** → **Adicionar à Tela de Início**.
- **Android (Chrome):** menu **⋮** → **Instalar app** / **Adicionar à tela inicial**.

Toque no ícone criado e use offline. Quando houver internet, o botão **↻ Atualizar** busca a base mais nova;
offline, ele continua abrindo a última versão baixada.

> Requer HTTPS — o GitHub Pages já serve em HTTPS, então funciona direto.

### Opção 2 — Baixar um arquivo único

No site, clique em **⤓ Baixar offline** para gerar `bulalivre-offline.html` com a base embutida — um único
arquivo que abre sem internet (melhor no computador). Para atualizar a cópia, baixe de novo.

## Observações legais

A base usada é o **Bulário Eletrônico / Dados Abertos da ANVISA**, de acesso livre por norma (RDC 885/2024).
Este projeto **não** copia nem redistribui conteúdo de bases proprietárias de terceiros.
