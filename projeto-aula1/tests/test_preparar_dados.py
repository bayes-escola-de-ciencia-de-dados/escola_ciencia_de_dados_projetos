import base64

import numpy as np
import pandas as pd
import pytest

from preparar_dados import SEM_CLASSIFICACAO, SEM_CONTRATO, STATUS, cadastro_fornecedores, derivar_status, preparar, raiz


def decodificar(col):
    return np.frombuffer(base64.b64decode(col["b64"]), dtype=np.dtype(col["dtype"]).newbyteorder("<"))


def test_raiz_usa_oito_primeiros_digitos():
    s = pd.Series(["12.345.678/0001-90", "12345678000290", "345678000190"])
    assert raiz(s).tolist() == ["12345678", "12345678", "00345678"]


def test_status_derivado_de_contrato_e_classificacao():
    pag = pd.DataFrame({
        "id_contrato": ["CT-1", "", "", "", ""],
        "classificacao_sem_contrato": ["Fora da Política", "Baixo valor", "Parcerias", "Fora da Política", ""],
    })
    assert list(derivar_status(pag)) == ["Com contrato", "Baixo valor", "Parcerias", "Fora da Política", "Não classificado"]


def test_raiz_herda_pior_status_e_nome_da_matriz():
    forn = pd.DataFrame({
        "cnpj_fornecedor": ["11111111000299", "11111111000190"],
        "nome_fornecedor": ["Filial SP", "Matriz Ltda"],
        "status_kys": ["Aprovado", "Negado"],
        "risco_financeiro": ["Baixo", "Médio"],
        "data_snapshot": ["2026-08-31", "2026-08-31"],
    })
    cad, snap = cadastro_fornecedores(forn)
    assert cad.loc["11111111", "nome"] == "Matriz Ltda"
    assert cad.loc["11111111", "kys"] == "Negado"
    assert cad.loc["11111111", "risco"] == "Médio"
    assert snap == "2026-08-31"


@pytest.fixture
def base_minima(tmp_path):
    pd.DataFrame([
        ["2026-08-10", "1000,50", "11111111000190", "CT-1", ""],
        ["2026-07-01", "200,00", "11111111000299", "", "Baixo valor"],
        ["2025-01-15", "300,00", "22222222000190", "", "Fora da Política"],
        ["2024-12-20", "50,00", "33333333000190", "", ""],
    ], columns=["data_pagamento", "valor_bruto", "cnpj_fornecedor", "id_contrato", "classificacao_sem_contrato"]).assign(
        categoria="TI", subcategoria_1="Software", subcategoria_2="SaaS", subcategoria_3="Licenças",
        gerencia_compras="Gerência TI", diretoria="DAC",
    ).to_csv(tmp_path / "pagamentos.csv", sep=";", index=False)
    pag = pd.read_csv(tmp_path / "pagamentos.csv", sep=";", dtype=str, keep_default_na=False)
    pag.loc[3, "subcategoria_3"] = ""
    pag.to_csv(tmp_path / "pagamentos.csv", sep=";", index=False)
    pd.DataFrame({
        "cnpj_fornecedor": ["11111111000190", "11111111000299", "22222222000190"],
        "nome_fornecedor": ["Alfa", "Alfa SP", "Beta"],
        "status_kys": ["Aprovado", "Aprovado", "Negado"],
        "risco_financeiro": ["Baixo", "Baixo", "Alto"],
        "data_snapshot": "2026-08-31",
    }).to_csv(tmp_path / "fornecedores.csv", sep=";", index=False)
    pd.DataFrame({
        "id_contrato": ["CT-1"], "descricao": ["Licenças Alfa"], "cnpj_fornecedor": ["11111111000190"],
        "data_inicio": ["2025-01-01"], "data_fim": ["2026-12-31"], "valor_contratado": ["5000,00"], "esteira_expressa": ["Sim"],
    }).to_csv(tmp_path / "contratos.csv", sep=";", index=False)
    pd.DataFrame({"id_contrato": ["CT-1", "CT-1"], "data_aporte": ["2025-06-01", "2026-01-10"], "valor_aporte": ["1000,00", "500,00"]}).to_csv(
        tmp_path / "aportes.csv", sep=";", index=False)
    return tmp_path


def test_soma_de_valores_preservada(base_minima):
    d = preparar(base_minima, "2026-09-15")
    assert decodificar(d["fato"]["colunas"]["valor"]).sum() == pytest.approx(1550.50)
    assert decodificar(d["fato"]["colunas"]["n_pagamentos"]).sum() == 4


def test_filiais_viram_um_fornecedor_e_cnpj_sem_cadastro_e_sinalizado(base_minima):
    d = preparar(base_minima, "2026-09-15")
    nomes = d["dims"]["fornecedor"]
    assert "Alfa" in nomes and "Alfa SP" not in nomes
    assert "CNPJ 33333333" in nomes
    i = nomes.index("CNPJ 33333333")
    assert d["dims"]["kys"][d["fornecedores"]["kys"][i]] == "Sem informação"


def test_status_no_fato(base_minima):
    d = preparar(base_minima, "2026-09-15")
    st = decodificar(d["fato"]["colunas"]["status"])
    v = decodificar(d["fato"]["colunas"]["valor"])
    por_status = {STATUS[s]: v[st == s].sum() for s in np.unique(st)}
    assert por_status == pytest.approx({"Com contrato": 1000.50, "Baixo valor": 200.0, "Fora da Política": 300.0, "Não classificado": 50.0})


def test_periodo_e_contrato(base_minima):
    d = preparar(base_minima, "2026-09-15")
    assert d["meta"]["ultimo_mes"] == "2026-08"
    assert d["dims"]["mes"][0] == "2024-12" and len(d["dims"]["mes"]) == 21
    assert d["dims"]["contrato"] == [SEM_CONTRATO, "CT-1"]
    assert d["contratos"]["consumo_12m"][1] == pytest.approx(1000.50)
    assert d["meta"]["base_percentual"] == "total"
    assert d["meta"]["inicio_base"] == "2024-12-20"
    assert d["versao_contrato"] == "3.0"


def test_contrato_no_fato(base_minima):
    d = preparar(base_minima, "2026-09-15")
    k = decodificar(d["fato"]["colunas"]["contrato"])
    v = decodificar(d["fato"]["colunas"]["valor"])
    assert v[k == 1].sum() == pytest.approx(1000.50)
    assert v[k == 0].sum() == pytest.approx(550.0)


def test_atributos_do_contrato(base_minima):
    c = preparar(base_minima, "2026-09-15")["contratos"]
    assert c["consumido"][1] == pytest.approx(1000.50)
    assert c["valor_contratado"][1] == pytest.approx(5000.0)
    assert c["n_aportes"][1] == 2 and c["valor_aportes"][1] == pytest.approx(1500.0)
    assert c["esteira"][1] == 1
    assert c["inicio_antes_base"][1] == 0
    assert c["aportes"]["data"] == ["2025-06-01", "2026-01-10"]
    anos = c["anos"]
    por_ano = dict(zip(anos, decodificar(c["consumo_ano"]).reshape(-1, len(anos))[1]))
    assert por_ano[2026] == pytest.approx(1000.50) and por_ano[2025] == 0


def test_saldo_derivado(base_minima):
    c = preparar(base_minima, "2026-09-15")["contratos"]
    saldo = c["valor_contratado"][1] + c["valor_aportes"][1] - c["consumido"][1]
    assert saldo == pytest.approx(5499.50)


def test_contrato_iniciado_antes_da_base(base_minima):
    ctr = pd.read_csv(base_minima / "contratos.csv", sep=";", dtype=str, keep_default_na=False)
    ctr.loc[0, "data_inicio"] = "2020-03-01"
    ctr.to_csv(base_minima / "contratos.csv", sep=";", index=False)
    assert preparar(base_minima, "2026-09-15")["contratos"]["inicio_antes_base"][1] == 1


def test_nivel_vazio_vira_sem_classificacao_com_pai(base_minima):
    d = preparar(base_minima, "2026-09-15")
    assert SEM_CLASSIFICACAO in d["dims"]["sub3"]
    i = d["dims"]["sub3"].index(SEM_CLASSIFICACAO)
    assert d["dims"]["sub2"][d["hierarquia"]["sub3"][i]] == "SaaS"


def test_aportes_opcional(base_minima):
    (base_minima / "aportes.csv").unlink()
    c = preparar(base_minima, "2026-09-15")["contratos"]
    assert c["n_aportes"][1] == 0
