import argparse
import json
import logging
from datetime import date
from pathlib import Path

from comum import RAIZ, configurar_log
from injetar_painel import injetar, validar
from preparar_dados import preparar

log = logging.getLogger("gerar_painel")

TEMPLATES = [("painel_template.html", "painel"), ("painel_classico.html", "painel_classico")]


def main():
    configurar_log("gerar_painel")
    p = argparse.ArgumentParser(description="Gera o painel a partir das 3 tabelas de entrada")
    p.add_argument("--base", default=str(RAIZ / "dados" / "entrada"))
    p.add_argument("--data-atualizacao", default=date.today().isoformat())
    p.add_argument("--saida", default=str(RAIZ / "saida" / "painel.html"))
    p.add_argument("--url-dados", default="dados.json", help="caminho do JSON que o .aspx lê no SharePoint (relativo à página ou absoluto no site)")
    a = p.parse_args()
    log.info("inicio base=%s data_atualizacao=%s", a.base, a.data_atualizacao)
    dados = preparar(Path(a.base), a.data_atualizacao)
    validar(dados)
    saida = Path(a.saida)
    sharepoint = saida.parent / "sharepoint"
    sharepoint.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":"))
    saida.with_suffix(".json").write_text(texto, encoding="utf-8")
    (sharepoint / Path(a.url_dados).name).write_text(texto, encoding="utf-8")
    lib = RAIZ / "vendor" / "echarts.min.js"
    for template, nome in TEMPLATES:
        origem = RAIZ / "src" / "template" / template
        html = saida if nome == "painel" else saida.with_name(nome + ".html")
        injetar(origem, lib, dados, html)
        injetar(origem, lib, dados, sharepoint / f"{nome}.aspx", a.url_dados)
    log.info("SharePoint: publicar a pasta %s (dados em %s)", sharepoint, a.url_dados)
    log.info("fim")


if __name__ == "__main__":
    main()
