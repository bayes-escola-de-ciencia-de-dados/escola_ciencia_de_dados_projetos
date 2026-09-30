import argparse
import logging
import re
from pathlib import Path

from comum import RAIZ, configurar_log

log = logging.getLogger("sincronizar_templates")

ORIGEM = RAIZ / "src" / "template" / "painel_template.html"
DESTINOS = [RAIZ / "src" / "template" / "painel_classico.html"]
BLOCOS = [("/*__INICIO_CSS_COMPARTILHADO__*/", "/*__FIM_CSS_COMPARTILHADO__*/"),
          ("/*__INICIO_COMPARTILHADO__*/", "/*__FIM_COMPARTILHADO__*/"),
          ("/*__INICIO_CARREGADOR__*/", "/*__FIM_CARREGADOR__*/")]


def bloco(texto, ini, fim):
    m = re.search(re.escape(ini) + r"(.*?)" + re.escape(fim), texto, re.S)
    if not m:
        raise ValueError(f"marcadores {ini} / {fim} não encontrados")
    return m


def sincronizar(origem, destino, verificar=False):
    fonte, alvo = origem.read_text(encoding="utf-8"), destino.read_text(encoding="utf-8")
    novo = alvo
    for ini, fim in BLOCOS:
        conteudo = bloco(fonte, ini, fim).group(1)
        m = bloco(novo, ini, fim)
        novo = novo[:m.start(1)] + conteudo + novo[m.end(1):]
    if novo == alvo:
        log.info("%s já está sincronizado", destino.name)
        return True
    if verificar:
        log.warning("%s difere de %s nos blocos compartilhados", destino.name, origem.name)
        return False
    destino.write_text(novo, encoding="utf-8")
    log.info("%s atualizado a partir de %s", destino.name, origem.name)
    return True


def main():
    configurar_log("sincronizar_templates")
    p = argparse.ArgumentParser(description="Copia os blocos compartilhados do painel_template para os demais templates")
    p.add_argument("--verificar", action="store_true", help="só verifica, sem alterar arquivos")
    a = p.parse_args()
    ok = all(sincronizar(ORIGEM, d, a.verificar) for d in DESTINOS)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
