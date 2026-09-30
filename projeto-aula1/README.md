# Spend Analysis

Painel HTML de análise de gastos para compradores, gerentes e executivos de compras. Conta a história do spend em 5 capítulos (quanto gastamos, com quem, com que proteção, com que risco, onde agir), vista por categoria, diretoria, fornecedor ou contrato, com a ficha de cada contrato (consumo, saldo, aportes, áreas pagadoras)

Arquivo único, abre no navegador sem internet e sem instalação

## Como gerar o painel

```
pip install -r requirements.txt
python src/pipeline/gerar_painel.py --base dados/entrada --data-atualizacao AAAA-MM-DD
```

Saem dois painéis com os mesmos dados: `saida/painel.html` (história em 5 capítulos) e `saida/painel_classico.html` (10 abas, no formato do painel anterior). Os logs ficam em `saida/logs/`

## Publicação no SharePoint

`saida/sharepoint/` traz os dois painéis em .aspx e o `dados.json`. O .aspx lê o JSON ao abrir ([decisão 0017](docs/decisoes/0017-dados-em-arquivo-no-sharepoint.md)):

- Primeira publicação ou mudança de layout: subir os .aspx e o `dados.json` para a mesma pasta da biblioteca
- Atualização de dados: substituir só o `dados.json`
- JSON em outro local do site: `--url-dados /sites/<site>/<biblioteca>/dados.json`

Para testar sem a base real:

```
python exemplos/gerar_base_exemplo.py
python src/pipeline/gerar_painel.py --base exemplos/base_exemplo
```

## Estrutura

```
src/template/     painel_template.html (canônico) e painel_classico.html
src/pipeline/     preparar_dados, injetar_painel, gerar_painel, sincronizar_templates, comum (log)
vendor/           ECharts 5.6.0 (embutido no painel)
exemplos/         gerador e base fictícia no formato de entrada
tests/            testes das regras do pipeline (python -m pytest tests)
docs/             documentação e registro de decisões
dados/entrada/    base real (ignorada pelo git)
saida/            painel gerado e logs (ignorada pelo git)
```

## Documentação

| Documento | Responde |
|---|---|
| [01 - Especificação](docs/01_especificacao.md) | O que o painel mostra, para quem e por quê |
| [02 - Base de entrada](docs/02_base_de_entrada.md) | Como devem vir as 3 tabelas |
| [03 - Contrato de dados](docs/03_contrato_de_dados.md) | Formato do arquivo entre pipeline e template |
| [04 - Template](docs/04_template.md) | Como o HTML está organizado e como editar |
| [05 - Pipeline](docs/05_pipeline.md) | Estrutura lógica de cada script |
| [06 - Como evoluir](docs/06_como_evoluir.md) | O que atualizar a cada tipo de mudança e checklist |
| [Backlog](docs/backlog.md) | Perguntas e ideias para versões futuras |
| [Decisões](docs/decisoes/README.md) | Por que as coisas são como são |
| [CHANGELOG](CHANGELOG.md) | O que mudou em cada versão |

## Regras do repositório

Detalhes em [06 - Como evoluir](docs/06_como_evoluir.md)

- Dados reais nunca entram no git: ficam em `dados/entrada/`, que é ignorada
- Uma fonte de verdade por assunto: cada documento acima cobre um tema e os outros apontam para ele
- Mudança de regra vira um registro em `docs/decisoes/`; mudança visível entra no CHANGELOG
- Toda versão publicada recebe uma tag (`git tag -a vX.Y`)
