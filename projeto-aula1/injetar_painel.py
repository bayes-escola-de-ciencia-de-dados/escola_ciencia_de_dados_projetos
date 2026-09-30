import argparse
import html as htmllib
import json
import logging
from pathlib import Path

from comum import RAIZ, configurar_log

log = logging.getLogger("injetar_painel")

MARCA_LIB = "/*__ECHARTS_LIB__*/"
MARCA_DADOS = "__SPEND_DATA__"
MARCA_URL = "__SPEND_URL__"
CAMPOS = ["versao_contrato", "meta", "dims", "hierarquia", "fornecedores", "fato", "contratos"]


def validar(dados):
    faltando = [c for c in CAMPOS if c not in dados]
    if faltando:
        raise ValueError(f"campos ausentes no contrato de dados: {faltando}")
    n = dados["fato"]["n_linhas"]
    for nome, col in dados["fato"]["colunas"].items():
        if isinstance(col, list) and len(col) != n:
            raise ValueError(f"coluna {nome} com {len(col)} linhas, esperado {n}")
    log.info("contrato ok: versao=%s linhas=%d", dados["versao_contrato"], n)


def injetar(template, lib, dados, saida, url_dados=None):
    html = Path(template).read_text(encoding="utf-8")
    for marca in (MARCA_LIB, MARCA_DADOS, MARCA_URL):
        if html.count(marca) != 1:
            raise ValueError(f"marcador {marca} deve aparecer exatamente 1 vez no template")
    js = Path(lib).read_text(encoding="utf-8").replace("</script", "<\\/script")
    if url_dados:
        payload, url = "", htmllib.escape(url_dados, quote=True)
    else:
        payload, url = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"), ""
    html = html.replace(MARCA_LIB, js).replace(MARCA_URL, url).replace(MARCA_DADOS, payload)
    Path(saida).write_text(html, encoding="utf-8")
    log.info("painel gerado: %s (%.1f MB)", saida, Path(saida).stat().st_size / 1e6)


def main():
    configurar_log("injetar_painel")
    p = argparse.ArgumentParser()
    p.add_argument("--template", default=str(RAIZ / "src" / "template" / "painel_template.html"))
    p.add_argument("--lib", default=str(RAIZ / "vendor" / "echarts.min.js"))
    p.add_argument("--dados", default=str(RAIZ / "saida" / "dados_painel.json"))
    p.add_argument("--saida", default=str(RAIZ / "saida" / "painel.html"))
    a = p.parse_args()
    dados = json.loads(Path(a.dados).read_text(encoding="utf-8"))
    validar(dados)
    Path(a.saida).parent.mkdir(parents=True, exist_ok=True)
    injetar(a.template, a.lib, dados, a.saida)


if __name__ == "__main__":
    main()
