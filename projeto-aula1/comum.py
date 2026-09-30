import logging
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PASTA_LOGS = RAIZ / "saida" / "logs"


def configurar_log(nome, pasta=PASTA_LOGS):
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f"{datetime.now():%Y%m%d_%H%M%S}_{nome}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(arquivo, encoding="utf-8")],
        force=True,
    )
    logging.getLogger(nome).info("log gravado em %s", arquivo)
    return arquivo
