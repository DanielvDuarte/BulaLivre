#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baixa o dataset de medicamentos dos Dados Abertos da ANVISA e gera o bulas.json
consumido pelo app (index.html).

- Produtos + laboratórios + princípio ativo + classe vêm da ANVISA (dados abertos).
- Os "sintomas" (para a busca por sintoma) são resolvidos a partir do princípio
  ativo usando build/mapa_sintomas.json (editável).

Uso:
    python build/update_data.py
    python build/update_data.py --url "https://.../DADOS_ABERTOS_MEDICAMENTOS.csv"
    ANVISA_CSV_URL=... python build/update_data.py

Se o layout/URL do dataset da ANVISA mudar, ajuste --url (ou a variável de ambiente
ANVISA_CSV_URL) e, se necessário, as listas de nomes de coluna em COLS abaixo.
"""
import argparse, csv, io, json, os, re, sys, unicodedata, datetime, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# URL padrão do dataset de medicamentos registrados (Dados Abertos ANVISA).
# Pode ser sobrescrita por --url ou pela variável ANVISA_CSV_URL.
DEFAULT_URL = os.environ.get(
    "ANVISA_CSV_URL",
    "https://dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv",
)

# Palavras-chave para localizar cada coluna (comparação sem acento/minúscula, por "contém").
COLS = {
    "nome":  ["nome_produto", "produto", "nome comercial", "nome"],
    "lab":   ["empresa_detentora", "razao_social", "nome_empresa", "empresa", "detentor", "laboratorio", "fabricante"],
    "pa":    ["principio_ativo", "principio ativo", "substancia", "ativo"],
    "classe":["classe_terapeutica", "classe terapeutica", "classe"],
    "tarja": ["tarja", "tipo_receita", "restricao_prescricao", "venda"],
    "situ":  ["situacao_registro", "situacao"],
    "cat":   ["categoria_regulatoria", "categoria"],
}

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn")

def norm(s):
    return strip_accents(str(s)).lower().strip()

def fetch(url):
    print(f"[info] baixando: {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": "vademecum-updater/1.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read()
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace")

def sniff_delim(sample):
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,|\t").delimiter
    except Exception:
        return ";"  # datasets da ANVISA costumam usar ponto e vírgula

def find_cols(header):
    nmap = {norm(h): h for h in header}
    resolved = {}
    for key, cands in COLS.items():
        hit = None
        for cand in cands:
            for nh, orig in nmap.items():
                if cand in nh:
                    hit = orig
                    break
            if hit:
                break
        resolved[key] = hit
    return resolved

def classify_tipo(tarja, categoria):
    t = norm(tarja) + " " + norm(categoria)
    if "preta" in t or "b1" in t or "b2" in t or "a1" in t or "a2" in t or "a3" in t or "controle especial" in t:
        return "ctrl"
    if "vermelha" in t or "retencao" in t or "prescricao" in t or "sob prescricao" in t:
        return "presc"
    if "sem tarja" in t or "livre" in t or "isento" in t or "mip" in t:
        return "mip"
    return ""

def clean(s):
    return re.sub(r"\s+", " ", (s or "").strip())

def title_br(s):
    s = clean(s)
    return s.title() if s and s.isupper() else s

def clean_lab(s):
    s = clean(s)
    # remove CNPJ no início do nome da empresa (ex.: "61099966000112 - Sanofi...")
    s = re.sub(r"^\s*\d[\d./\-]{9,}\s*[-–]\s*", "", s)
    return title_br(s)

def resolve_sintomas(pa_text, mapa):
    npa = norm(pa_text)
    if not npa:
        return []
    out = []
    for key, sintomas in mapa.items():
        if key.startswith("_"):
            continue
        if key in npa:
            for s in sintomas:
                if s not in out:
                    out.append(s)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=DEFAULT_URL)
    ap.add_argument("--out", default=os.path.join(ROOT, "bulas.json"))
    ap.add_argument("--mapa", default=os.path.join(HERE, "mapa_sintomas.json"))
    ap.add_argument("--max", type=int, default=0, help="limite de produtos (0 = sem limite)")
    args = ap.parse_args()

    with open(args.mapa, encoding="utf-8") as f:
        mapa = json.load(f)

    text = fetch(args.url)
    delim = sniff_delim(text[:5000])
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    rows = iter(reader)
    header = next(rows)
    cols = find_cols(header)
    print(f"[info] delimitador={delim!r}  colunas detectadas={cols}", file=sys.stderr)
    if not cols["nome"]:
        print("[erro] não encontrei a coluna de NOME do produto. Ajuste COLS/--url.", file=sys.stderr)
        sys.exit(2)
    idx = {k: (header.index(v) if v in header else None) for k, v in cols.items()}

    def cell(row, key):
        i = idx.get(key)
        return row[i] if (i is not None and i < len(row)) else ""

    seen, produtos = set(), []
    total_rows = 0
    for row in rows:
        total_rows += 1
        if not row:
            continue
        situ = norm(cell(row, "situ"))
        if situ and ("valido" not in situ and "ativo" not in situ and "vigente" not in situ):
            continue  # pula registros cancelados/vencidos quando a coluna existe
        nome = title_br(cell(row, "nome"))
        if not nome:
            continue
        lab = clean_lab(cell(row, "lab"))
        pa = clean(cell(row, "pa"))
        key = (norm(nome), norm(lab))
        if key in seen:
            continue
        seen.add(key)
        produtos.append({
            "nome": nome,
            "laboratorio": lab,
            "pa": pa,
            "classe": title_br(cell(row, "classe")),
            "tipo": classify_tipo(cell(row, "tarja"), cell(row, "cat")),
            "sintomas": resolve_sintomas(pa, mapa),
        })
        if args.max and len(produtos) >= args.max:
            break

    produtos.sort(key=lambda p: norm(p["nome"]))
    now = datetime.datetime.now(datetime.timezone.utc)
    out = {
        "versao": now.strftime("%Y-%m-%d"),
        "atualizado_em": now.isoformat(timespec="seconds"),
        "fonte": "ANVISA — Dados Abertos (medicamentos registrados)",
        "fonte_url": args.url,
        "total": len(produtos),
        "produtos": produtos,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    com_sintoma = sum(1 for p in produtos if p["sintomas"])
    print(f"[ok] {len(produtos)} produtos ({com_sintoma} com sintomas) de {total_rows} linhas "
          f"-> {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
