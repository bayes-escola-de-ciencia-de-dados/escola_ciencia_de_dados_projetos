import argparse
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "pipeline"))
from comum import RAIZ, configurar_log

log = logging.getLogger("gerar_base_exemplo")

GERENCIAS = ["Gerência TI e Telecom", "Gerência Serviços", "Gerência Facilities", "Gerência Marketing", "Gerência Indiretos"]
DIRETORIAS = ["DAC", "Dir Plataformas Digitais", "Dir Parcerias", "Dir Marketing", "Dir Operações e Pagamentos",
              "Dir Jornadas", "Dir Infraestrutura", "Dir Arquitetura", "Dir Crédito", "Dir Jurídico", "Dir Pessoas", "Dir Riscos"]
ARVORE = {
    "Tecnologia da Informação e Telecom": (0, ["Software", "Infraestrutura", "Telecom", "Serviços de TI"]),
    "Serviços Profissionais": (1, ["Consultoria", "BPO", "Auditoria"]),
    "Construção e Manutenção": (2, ["Obras civis", "Manutenção predial"]),
    "Engenharia e Pesquisa": (1, ["Engenharia", "Pesquisa de mercado"]),
    "Segurança": (2, ["Vigilância", "Combate a incêndio", "Controle de acesso"]),
    "Transporte e Logística": (4, ["Transporte de valores", "Armazenagem"]),
    "Marketing e Eventos": (3, ["Mídia", "Eventos", "Brindes"]),
    "Viagens": (4, ["Passagens", "Hospedagem"]),
    "Impressão e Editorial": (3, ["Impressão", "Design"]),
    "Mobiliário": (2, ["Mobiliário"]),
    "Energia": (2, ["Energia elétrica"]),
    "Tributos e Taxas": (4, ["Tributos"]),
}
PARCERIAS = {"Marketing e Eventos"}
NOMES = ["Alfa", "Beta", "Gama", "Delta", "Sigma", "Ômega", "Atlas", "Vértice", "Horizonte", "Prisma", "Núcleo",
         "Aurora", "Zênite", "Órbita", "Vetor", "Pilar", "Rota", "Elo", "Farol", "Âncora", "Lume", "Cume", "Sol", "Mar"]
TIPOS = ["Soluções", "Serviços", "Tecnologia", "Sistemas", "Consultoria", "Engenharia", "Logística", "Digital", "Comercial"]


def gerar(n_pag, seed, inicio, fim):
    rng = np.random.default_rng(seed)
    subs = [(c, s1) for c, (_, ss) in ARVORE.items() for s1 in ss]
    n_forn = max(150, min(1200, n_pag // 25))
    nomes = [f"{NOMES[i % len(NOMES)]} {TIPOS[(i // len(NOMES)) % len(TIPOS)]}{'' if i < 216 else ' ' + str(i // 216 + 1)} Ltda" for i in range(n_forn)]
    raiz = rng.choice(np.arange(10_000_000, 99_999_999), n_forn, replace=False)
    peso = rng.pareto(1.15, n_forn) + 0.03
    peso /= peso.sum()
    forn_sub = rng.integers(0, len(subs), n_forn)
    forn_dir = rng.choice(len(DIRETORIAS), (n_forn, 3))
    prop_cat = rng.uniform(0.55, 0.97, len(subs))
    tem_ctr = rng.random(n_forn) < np.minimum(0.98, prop_cat[forn_sub] + 0.25 * (peso > np.quantile(peso, 0.8)))

    fornecedores, filiais = [], []
    for i in range(n_forn):
        k = 1 + (rng.random() < 0.25) + (rng.random() < 0.1)
        cnpjs = [f"{raiz[i]:08d}{j + 1:04d}{rng.integers(10, 99)}" for j in range(k)]
        filiais.append(cnpjs)
        kys = "Negado" if rng.random() < 0.02 else "Aprovado"
        risco = rng.choice(["Baixo", "Médio", "Alto", "Sem avaliação"], p=[0.66, 0.26, 0.04, 0.04])
        for c in cnpjs:
            fornecedores.append({"cnpj_fornecedor": c, "nome_fornecedor": nomes[i], "status_kys": kys,
                                 "risco_financeiro": risco, "data_snapshot": fim.isoformat()})

    contratos = []
    ctr_por_forn = {}
    hoje = date(2026, 9, 27)
    for i in np.where(tem_ctr)[0]:
        ids = []
        for j in range(1 + (rng.random() < 0.3)):
            cid = f"CT-{i:04d}-{j + 1}"
            ini = inicio + timedelta(days=int(rng.integers(-500, 400)))
            dfim = hoje + timedelta(days=int(rng.choice([-20, 5, 18, 40, 75, 110, 150, 175, 260, 400, 620])))
            contratos.append({"id_contrato": cid, "descricao": f"{subs[forn_sub[i]][1]} - {nomes[i]}",
                              "cnpj_fornecedor": filiais[i][0], "data_inicio": ini.isoformat(),
                              "data_fim": dfim.isoformat(), "valor_contratado": 0.0,
                              "esteira_expressa": "Sim" if rng.random() < 0.25 else "Não"})
            ids.append(cid)
        ctr_por_forn[i] = ids

    f = rng.choice(n_forn, n_pag, p=peso)
    dias = (fim - inicio).days
    t = rng.random(n_pag) ** 0.75
    dt = [inicio + timedelta(days=int(x * dias)) for x in t]
    valor = np.round(rng.lognormal(9.6, 1.7, n_pag), 2)
    sub_idx = np.where(rng.random(n_pag) < 0.85, forn_sub[f], rng.integers(0, len(subs), n_pag))
    dir_idx = forn_dir[f, rng.integers(0, 3, n_pag)]
    linhas = []
    for k in range(n_pag):
        i = f[k]
        c, s1 = subs[sub_idx[k]]
        s2 = f"{s1} - Linha {1 + (k % 2)}" if sum(map(ord, s1)) % 10 else ""
        s3 = f"{s2}.{1 + (k % 3 == 0)}" if s2 and sum(map(ord, s1)) % 5 else ""
        idc, cls = "", ""
        u = rng.random()
        if i in ctr_por_forn and u < 0.95 and sub_idx[k] == forn_sub[i]:
            idc = ctr_por_forn[i][k % len(ctr_por_forn[i])]
        elif u > 0.992:
            cls = ""
        elif c in PARCERIAS and u < 0.95:
            cls = "Parcerias"
        elif valor[k] < 15000:
            cls = "Baixo valor"
        else:
            cls = "Fora da Política"
        linhas.append({"data_pagamento": dt[k].isoformat(), "valor_bruto": valor[k],
                       "cnpj_fornecedor": filiais[i][k % len(filiais[i])], "categoria": c,
                       "subcategoria_1": s1, "subcategoria_2": s2, "subcategoria_3": s3,
                       "gerencia_compras": GERENCIAS[ARVORE[c][0]], "diretoria": DIRETORIAS[dir_idx[k]],
                       "id_contrato": idc, "classificacao_sem_contrato": cls})
    pag, ctr = pd.DataFrame(linhas), pd.DataFrame(contratos)
    consumo = pag.groupby("id_contrato")["valor_bruto"].sum()
    ctr["valor_contratado"] = [round(float(consumo.get(c, 0) * rng.uniform(0.55, 1.4) + rng.lognormal(12, 0.8)), 2) for c in ctr["id_contrato"]]
    aportes = []
    for _, c in ctr.iterrows():
        for _ in range(int(rng.choice([0, 0, 0, 1, 1, 2, 3]))):
            ini = date.fromisoformat(max(c["data_inicio"], inicio.isoformat()))
            dt_ap = ini + timedelta(days=int(rng.integers(30, max(31, (fim - ini).days))))
            aportes.append({"id_contrato": c["id_contrato"], "data_aporte": min(dt_ap, fim).isoformat(),
                            "valor_aporte": round(float(c["valor_contratado"] * rng.uniform(0.08, 0.3)), 2)})
    return pag, pd.DataFrame(fornecedores), ctr, pd.DataFrame(aportes)


def main():
    configurar_log("gerar_base_exemplo")
    p = argparse.ArgumentParser()
    p.add_argument("--pagamentos", type=int, default=30000)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--saida", default=str(RAIZ / "exemplos" / "base_exemplo"))
    a = p.parse_args()
    pag, forn, ctr, apt = gerar(a.pagamentos, a.seed, date(2022, 1, 1), date(2026, 8, 31))
    out = Path(a.saida)
    out.mkdir(parents=True, exist_ok=True)
    pag.to_csv(out / "pagamentos.csv", index=False, sep=";", decimal=",")
    forn.to_csv(out / "fornecedores.csv", index=False, sep=";")
    ctr.to_csv(out / "contratos.csv", index=False, sep=";", decimal=",")
    apt.to_csv(out / "aportes.csv", index=False, sep=";", decimal=",")
    log.info("pagamentos=%d fornecedores(cnpj)=%d contratos=%d aportes=%d pasta=%s", len(pag), len(forn), len(ctr), len(apt), out)


if __name__ == "__main__":
    main()
