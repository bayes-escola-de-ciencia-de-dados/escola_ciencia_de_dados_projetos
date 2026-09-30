import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
TEMPLATE = (RAIZ / "src" / "template" / "painel_template.html").read_text(encoding="utf-8")
CLASSICO = (RAIZ / "src" / "template" / "painel_classico.html").read_text(encoding="utf-8")
BLOCOS = [("/*__INICIO_CSS_COMPARTILHADO__*/", "/*__FIM_CSS_COMPARTILHADO__*/"),
          ("/*__INICIO_COMPARTILHADO__*/", "/*__FIM_COMPARTILHADO__*/"),
          ("/*__INICIO_CARREGADOR__*/", "/*__FIM_CARREGADOR__*/")]
MARKDOWNS = [RAIZ / "README.md", RAIZ / "CHANGELOG.md"] + sorted(DOCS.rglob("*.md"))


def ler(p):
    return p.read_text(encoding="utf-8")


def test_versao_do_contrato_igual_no_codigo_e_no_documento():
    codigo = re.search(r'VERSAO_CONTRATO = "([\d.]+)"', ler(RAIZ / "src" / "pipeline" / "preparar_dados.py")).group(1)
    doc = re.search(r'`versao_contrato`\s*\|\s*`"([\d.]+)"`', ler(DOCS / "03_contrato_de_dados.md")).group(1)
    assert codigo == doc


def test_toda_decisao_esta_no_indice():
    indice = ler(DOCS / "decisoes" / "README.md")
    faltando = [p.name for p in (DOCS / "decisoes").glob("[0-9]*.md") if f"({p.name})" not in indice]
    assert not faltando, f"decisões fora do índice: {faltando}"


@pytest.mark.parametrize("arquivo", MARKDOWNS, ids=lambda p: str(p.relative_to(RAIZ)))
def test_links_entre_documentos_existem(arquivo):
    quebrados = []
    for alvo in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", ler(arquivo)):
        if alvo.startswith(("http://", "https://", "mailto:")):
            continue
        if not (arquivo.parent / alvo).exists():
            quebrados.append(alvo)
    assert not quebrados, f"links quebrados: {quebrados}"


def test_filtros_do_template_estao_na_especificacao():
    bloco = re.search(r"const FILTROS = \[(.*?)\];", TEMPLATE, re.S).group(1)
    nomes = re.findall(r'nome:\s*"([^"]+)"', bloco) + ["Período"]
    espec = ler(DOCS / "01_especificacao.md")
    faltando = [n for n in nomes if n not in espec]
    assert not faltando, f"filtros sem documentação: {faltando}"


@pytest.mark.parametrize("texto", [TEMPLATE, CLASSICO], ids=["painel_template", "painel_classico"])
def test_marcadores_do_template_aparecem_uma_vez(texto):
    for marcador in ["/*__ECHARTS_LIB__*/", "__SPEND_DATA__", "__SPEND_URL__"] + [m for par in BLOCOS for m in par]:
        assert texto.count(marcador) == 1, marcador


@pytest.mark.parametrize("ini,fim", BLOCOS, ids=["css", "js", "carregador"])
def test_blocos_compartilhados_iguais_nos_dois_templates(ini, fim):
    padrao = re.escape(ini) + r"(.*?)" + re.escape(fim)
    assert re.search(padrao, TEMPLATE, re.S).group(1) == re.search(padrao, CLASSICO, re.S).group(1), \
        "rode python src/pipeline/sincronizar_templates.py"


def test_filtros_do_classico_iguais_ao_principal():
    filtros = lambda t: re.search(r"const FILTROS = \[(.*?)\];", t, re.S).group(1)
    assert filtros(TEMPLATE) == filtros(CLASSICO)


def test_changelog_comeca_por_nao_publicado():
    secoes = re.findall(r"^## (.+)$", ler(RAIZ / "CHANGELOG.md"), re.M)
    assert secoes and secoes[0].strip() == "Não publicado"
