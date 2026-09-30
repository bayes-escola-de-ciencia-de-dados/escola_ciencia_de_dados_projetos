import json

import pytest

from comum import RAIZ
from injetar_painel import injetar

LIB = RAIZ / "vendor" / "echarts.min.js"
DADOS = {"versao_contrato": "3.0", "meta": {"titulo": "a</script>b"}}


@pytest.fixture(params=["painel_template.html", "painel_classico.html"])
def template(request):
    return RAIZ / "src" / "template" / request.param


def test_modo_embutido_leva_os_dados_no_html(template, tmp_path):
    saida = tmp_path / "painel.html"
    injetar(template, LIB, DADOS, saida)
    html = saida.read_text(encoding="utf-8")
    assert 'data-url=""' in html
    assert '"versao_contrato":"3.0"' in html
    assert "a<\\/script>b" in html
    assert "__SPEND_" not in html


def test_modo_arquivo_aponta_para_o_json_sem_embutir(template, tmp_path):
    saida = tmp_path / "painel.aspx"
    injetar(template, LIB, DADOS, saida, "/sites/compras/Dados/dados.json")
    html = saida.read_text(encoding="utf-8")
    assert 'data-url="/sites/compras/Dados/dados.json"></script>' in html
    assert "versao_contrato" not in html
    assert "__SPEND_" not in html


def test_url_com_caracteres_especiais_e_escapada(template, tmp_path):
    saida = tmp_path / "painel.aspx"
    injetar(template, LIB, DADOS, saida, 'dados.json?a=1&b="x"')
    assert 'data-url="dados.json?a=1&amp;b=&quot;x&quot;"' in saida.read_text(encoding="utf-8")
