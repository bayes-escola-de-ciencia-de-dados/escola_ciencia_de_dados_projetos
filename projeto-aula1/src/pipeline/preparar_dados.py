import argparse
import base64
import json
import logging
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from comum import RAIZ, configurar_log

log = logging.getLogger("preparar_dados")

VERSAO_CONTRATO = "3.0"
STATUS = ["Com contrato", "Baixo valor", "Parcerias", "Fora da Política", "Não classificado"]
KYS = ["Aprovado", "Negado", "Pendente", "Sem informação"]
RISCO = ["Baixo", "Médio", "Alto", "Sem avaliação"]
ESTEIRA = ["Não", "Sim", "Sem informação"]
PIOR_KYS = {"Negado": 0, "Pendente": 1, "Sem informação": 2, "Aprovado": 3}
PIOR_RISCO = {"Alto": 0, "Médio": 1, "Sem avaliação": 2, "Baixo": 3}
HIERARQUIA = ["categoria", "subcategoria_1", "subcategoria_2", "subcategoria_3"]
NIVEIS = ["categoria", "sub1", "sub2", "sub3"]
SEM_CLASSIFICACAO = "Sem classificação"
SEM_CONTRATO = "(pagamentos sem contrato)"
ATRIB_MODA = ["gerencia", "categoria", "sub1", "sub2", "sub3", "diretoria"]


def b64(arr, dtype):
    a = np.ascontiguousarray(arr, dtype=np.dtype(dtype).newbyteorder("<"))
    return {"dtype": np.dtype(dtype).name, "b64": base64.b64encode(a.tobytes()).decode("ascii")}


def tipo_codigo(n):
    return "uint8" if n < 256 else "uint16" if n < 65536 else "uint32"


def ler(pasta):
    txt = {"cnpj_fornecedor": str, "id_contrato": str, "classificacao_sem_contrato": str}
    pag = pd.read_csv(pasta / "pagamentos.csv", sep=";", decimal=",", dtype=txt, keep_default_na=False)
    forn = pd.read_csv(pasta / "fornecedores.csv", sep=";", dtype=str, keep_default_na=False)
    ctr = pd.read_csv(pasta / "contratos.csv", sep=";", decimal=",", dtype={"id_contrato": str, "cnpj_fornecedor": str, "esteira_expressa": str}, keep_default_na=False)
    arq_apt = pasta / "aportes.csv"
    if arq_apt.exists():
        apt = pd.read_csv(arq_apt, sep=";", decimal=",", dtype={"id_contrato": str}, keep_default_na=False)
    else:
        log.warning("aportes.csv não encontrado - contratos sem aportes")
        apt = pd.DataFrame({"id_contrato": pd.Series(dtype=str), "data_aporte": pd.Series(dtype=str), "valor_aporte": pd.Series(dtype=float)})
    log.info("lidos pagamentos=%d fornecedores=%d contratos=%d aportes=%d", len(pag), len(forn), len(ctr), len(apt))
    return pag, forn, ctr, apt


def raiz(serie):
    return serie.str.replace(r"\D", "", regex=True).str.zfill(14).str[:8]


def cadastro_fornecedores(forn):
    forn = forn.assign(raiz=raiz(forn["cnpj_fornecedor"]), matriz=forn["cnpj_fornecedor"].str[8:12] == "0001")
    forn["kys_ord"] = forn["status_kys"].map(PIOR_KYS).fillna(2)
    forn["risco_ord"] = forn["risco_financeiro"].map(PIOR_RISCO).fillna(2)
    nome = forn.sort_values("matriz", ascending=False).groupby("raiz")["nome_fornecedor"].first()
    kys = forn.groupby("raiz")["kys_ord"].min().map({v: k for k, v in PIOR_KYS.items()})
    risco = forn.groupby("raiz")["risco_ord"].min().map({v: k for k, v in PIOR_RISCO.items()})
    snap = forn["data_snapshot"].max()
    cad = pd.DataFrame({"nome": nome, "kys": kys, "risco": risco})
    log.info("fornecedores por raiz=%d kys_negado=%d risco_alto=%d", len(cad), (cad.kys == "Negado").sum(), (cad.risco == "Alto").sum())
    return cad, snap


def derivar_status(pag):
    cls = pag["classificacao_sem_contrato"].str.strip()
    st = np.where(pag["id_contrato"].str.strip() != "", "Com contrato",
                  np.where(cls.isin(STATUS[1:4]), cls, "Não classificado"))
    return pd.Categorical(st, categories=STATUS)


def normalizar_hierarquia(pag):
    for col in HIERARQUIA:
        pag[col] = pag[col].astype(str).str.strip()
        vazios = pag[col] == ""
        if vazios.any():
            log.info("%s vazia em %d pagamentos -> '%s'", col, int(vazios.sum()), SEM_CLASSIFICACAO)
        pag.loc[vazios, col] = SEM_CLASSIFICACAO
    return pag


def codificar_hierarquia(pag):
    cod, dims, pais = {}, {}, {}
    anterior = None
    for n, nome in enumerate(NIVEIS):
        g = pag.groupby(HIERARQUIA[:n + 1], sort=True)
        cod[nome] = g.ngroup().to_numpy()
        chaves = [k if isinstance(k, tuple) else (k,) for k in g.size().index]
        dims[nome] = [str(k[-1]) for k in chaves]
        if anterior is not None:
            pais[nome] = [anterior[k[:-1]] for k in chaves]
        anterior = {k: i for i, k in enumerate(chaves)}
    return cod, dims, pais


def esteira_codigo(v):
    v = str(v).strip().lower()
    return 1 if v in {"sim", "s", "1", "true"} else 0 if v in {"não", "nao", "n", "0", "false"} else 2


def atributos_contratos(pag, ctr, apt, cod, idx_forn, anos, ini_12m, data_atualizacao, inicio_base):
    pc = pag[pag["id_contrato"] != ""]
    ctr = ctr.assign(id_contrato=ctr["id_contrato"].str.strip(), raiz=raiz(ctr["cnpj_fornecedor"]))
    ctr = ctr.drop_duplicates("id_contrato", keep="last").set_index("id_contrato")
    lim = (pd.Timestamp(data_atualizacao) - pd.Timedelta(days=60)).date().isoformat()
    ids = sorted(set(pc["id_contrato"]) | set(ctr.index[(ctr["data_fim"] >= lim) & ctr["raiz"].isin(idx_forn)]))
    sem_cadastro = sorted(set(pc["id_contrato"]) - set(ctr.index))
    if sem_cadastro:
        log.warning("contratos com pagamento e sem cadastro=%d (ex.: %s)", len(sem_cadastro), sem_cadastro[:3])
    nomes = [SEM_CONTRATO] + ids
    pos = {c: i for i, c in enumerate(nomes)}
    n = len(nomes)

    tmp = pd.DataFrame({k: cod[k] for k in ATRIB_MODA + ["fornecedor"]}, index=pag.index).loc[pc.index]
    tmp["id"] = pc["id_contrato"]
    moda = tmp.groupby("id")[ATRIB_MODA + ["fornecedor"]].agg(lambda s: int(s.mode().iloc[0]))
    consumido = pc.groupby("id_contrato")["valor_bruto"].sum()
    consumo12 = pc[pc["mes"] >= ini_12m].groupby("id_contrato")["valor_bruto"].sum()
    por_ano = pc.assign(ano=pc["mes"].str[:4].astype(int)).groupby(["id_contrato", "ano"])["valor_bruto"].sum()
    apt = apt.assign(id_contrato=apt["id_contrato"].astype(str).str.strip(), valor_aporte=pd.to_numeric(apt["valor_aporte"], errors="coerce").fillna(0.0))
    apt = apt[apt["id_contrato"].isin(pos)]
    aportes_n = apt.groupby("id_contrato").size()
    aportes_v = apt.groupby("id_contrato")["valor_aporte"].sum()

    at = {k: [None] * n for k in ["descricao", "data_inicio", "data_fim", "valor_contratado"]}
    at.update({k: [0] * n for k in ["fornecedor", "esteira", "n_aportes", "inicio_antes_base"]})
    at.update({k: [0.0] * n for k in ["valor_aportes", "consumido", "consumo_12m"]})
    at.update({k: [-1] * n for k in ATRIB_MODA})
    at["descricao"][0] = SEM_CONTRATO
    at["esteira"][0] = 2
    matriz_ano = np.zeros((n, len(anos)))
    for c in ids:
        i = pos[c]
        tem_cad = c in ctr.index
        if tem_cad:
            r = ctr.loc[c]
            at["descricao"][i] = str(r["descricao"])
            at["data_inicio"][i] = str(r["data_inicio"]) or None
            at["data_fim"][i] = str(r["data_fim"]) or None
            vc = pd.to_numeric(str(r["valor_contratado"]).replace(",", "."), errors="coerce")
            at["valor_contratado"][i] = None if pd.isna(vc) else round(float(vc), 2)
            at["esteira"][i] = esteira_codigo(r.get("esteira_expressa", ""))
            at["fornecedor"][i] = idx_forn.get(r["raiz"], int(moda.loc[c, "fornecedor"]) if c in moda.index else 0)
            at["inicio_antes_base"][i] = int(bool(at["data_inicio"][i]) and at["data_inicio"][i] < inicio_base)
        else:
            at["descricao"][i] = "Contrato sem cadastro"
            at["esteira"][i] = 2
            at["fornecedor"][i] = int(moda.loc[c, "fornecedor"])
        if c in moda.index:
            for k in ATRIB_MODA:
                at[k][i] = int(moda.loc[c, k])
        at["consumido"][i] = round(float(consumido.get(c, 0.0)), 2)
        at["consumo_12m"][i] = round(float(consumo12.get(c, 0.0)), 2)
        at["n_aportes"][i] = int(aportes_n.get(c, 0))
        at["valor_aportes"][i] = round(float(aportes_v.get(c, 0.0)), 2)
    for (c, a), v in por_ano.items():
        matriz_ano[pos[c], anos.index(a)] = v

    pares = tmp.assign(dir=tmp["diretoria"], v=pc["valor_bruto"], v12=np.where(pc["mes"] >= ini_12m, pc["valor_bruto"], 0.0)).groupby(["id", "dir"])[["v", "v12"]].sum().reset_index()
    at["anos"] = anos
    at["consumo_ano"] = b64(matriz_ano.ravel(), "float64")
    at["diretorias"] = {"contrato": b64(pares["id"].map(pos), tipo_codigo(n)), "diretoria": b64(pares["dir"], "uint16"), "valor": b64(pares["v"], "float64"), "valor_12m": b64(pares["v12"], "float64")}
    ap = apt.sort_values("data_aporte")
    at["aportes"] = {"contrato": ap["id_contrato"].map(pos).tolist(), "data": ap["data_aporte"].astype(str).tolist(), "valor": ap["valor_aporte"].round(2).tolist()}
    log.info("contratos=%d com_pagamento=%d com_aporte=%d esteira_sim=%d inicio_antes_base=%d",
             len(ids), len(set(pc["id_contrato"])), int((aportes_n > 0).sum()), at["esteira"].count(1), sum(at["inicio_antes_base"]))
    return nomes, pos, at


def preparar(pasta, data_atualizacao):
    pag, forn, ctr, apt = ler(pasta)
    cad, snap = cadastro_fornecedores(forn)
    pag["raiz"] = raiz(pag["cnpj_fornecedor"])
    pag["id_contrato"] = pag["id_contrato"].str.strip()
    faltando = ~pag["raiz"].isin(cad.index)
    if faltando.any():
        log.warning("pagamentos com fornecedor fora do cadastro=%d", int(faltando.sum()))
        novos = pag.loc[faltando, "raiz"].unique()
        cad = pd.concat([cad, pd.DataFrame({"nome": "CNPJ " + novos, "kys": "Sem informação", "risco": "Sem avaliação"}, index=novos)])
    pag["status"] = derivar_status(pag)
    pag["mes"] = pag["data_pagamento"].str[:7]
    ultimo_mes = pag["mes"].max()
    inicio_base = pag["data_pagamento"].min()
    log.info("status: %s", pag["status"].value_counts().to_dict())
    pag = normalizar_hierarquia(pag)

    meses = pd.period_range(pag["mes"].min(), ultimo_mes, freq="M").strftime("%Y-%m").tolist()
    anos = sorted({int(m[:4]) for m in meses})
    cod, dims, pais = codificar_hierarquia(pag)
    dims["mes"] = meses
    for col, nome in [("gerencia_compras", "gerencia"), ("diretoria", "diretoria")]:
        unicos = sorted(pag[col].unique())
        dims[nome] = unicos
        cod[nome] = pag[col].map({u: i for i, u in enumerate(unicos)}).to_numpy()
    cad = cad.sort_values("nome")
    raizes = cad.index.tolist()
    idx_forn = {r: i for i, r in enumerate(raizes)}
    dims["fornecedor"] = cad["nome"].tolist()
    dims["status"] = STATUS
    dims["kys"] = KYS
    dims["risco"] = RISCO
    dims["esteira"] = ESTEIRA
    cod["fornecedor"] = pag["raiz"].map(idx_forn).to_numpy()
    cod["mes"] = pag["mes"].map({m: i for i, m in enumerate(meses)}).to_numpy()
    cod["status"] = pag["status"].cat.codes.to_numpy()

    ini_12m = (pd.Period(ultimo_mes, "M") - 11).strftime("%Y-%m")
    nomes_ctr, pos_ctr, contratos = atributos_contratos(pag, ctr, apt, cod, idx_forn, anos, ini_12m, data_atualizacao, inicio_base)
    dims["contrato"] = nomes_ctr
    cod["contrato"] = pag["id_contrato"].map(lambda c: pos_ctr.get(c, 0)).to_numpy()

    grao = ["mes", "gerencia", "categoria", "sub1", "sub2", "sub3", "diretoria", "fornecedor", "status", "contrato"]
    if "enderecavel" in pag.columns:
        cod["enderecavel"] = pag["enderecavel"].astype(str).str.lower().isin(["1", "sim", "s", "true"]).astype(int).to_numpy()
        grao.append("enderecavel")
    df = pd.DataFrame({k: cod[k] for k in grao})
    df["valor"] = pag["valor_bruto"].astype(float).to_numpy()
    df["n_pagamentos"] = 1
    fato = df.groupby(grao, sort=False, as_index=False).agg(valor=("valor", "sum"), n_pagamentos=("n_pagamentos", "sum"))
    log.info("linhas pagamento=%d linhas fato=%d", len(pag), len(fato))
    colunas = {k: b64(fato[k], tipo_codigo(len(dims.get(k, [0, 1])))) for k in grao}
    colunas["valor"] = b64(fato["valor"], "float64")
    colunas["n_pagamentos"] = b64(fato["n_pagamentos"], "uint32")

    return {
        "versao_contrato": VERSAO_CONTRATO,
        "meta": {
            "titulo": "Painel Executivo",
            "titulo_destaque": "Spend Analysis",
            "subtitulo": "Análise de gastos orientada à redução de custos",
            "data_atualizacao": data_atualizacao,
            "data_snapshot_fornecedores": snap,
            "inicio_base": inicio_base,
            "ultimo_mes": ultimo_mes,
            "metas": {"cobertura_min": 0.80, "fora_politica_max": 0.10, "kys_min": 0.95, "saldo_alerta": 0.10},
            "janela_vencimento_dias": 180,
            "base_percentual": "enderecavel" if "enderecavel" in grao else "total",
            "rodape": "Spend Analysis · Valores nominais por data de pagamento",
        },
        "dims": dims,
        "hierarquia": pais,
        "fornecedores": {"raiz": raizes, "kys": [KYS.index(k) for k in cad["kys"]], "risco": [RISCO.index(r) for r in cad["risco"]]},
        "fato": {"n_linhas": int(len(fato)), "colunas": colunas},
        "contratos": contratos,
    }


def main():
    configurar_log("preparar_dados")
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=str(RAIZ / "dados" / "entrada"))
    p.add_argument("--data-atualizacao", default=date.today().isoformat())
    p.add_argument("--saida", default=str(RAIZ / "saida" / "dados_painel.json"))
    a = p.parse_args()
    dados = preparar(Path(a.base), a.data_atualizacao)
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.saida).write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    log.info("arquivo=%s (%.1f MB)", a.saida, Path(a.saida).stat().st_size / 1e6)


if __name__ == "__main__":
    main()
