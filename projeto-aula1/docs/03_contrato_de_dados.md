# 03 - Contrato de dados

Formato do JSON que o `preparar_dados.py` gera. No HTML, o `injetar_painel.py` o coloca no template (marcador `__SPEND_DATA__`); no SharePoint, ele vai no arquivo `dados.json`, que o .aspx busca ao abrir ([decisão 0017](decisoes/0017-dados-em-arquivo-no-sharepoint.md)). O ECharts entra no marcador `/*__ECHARTS_LIB__*/`

| Bloco | Conteúdo |
|---|---|
| `versao_contrato` | `"3.0"` |
| `meta` | `titulo`, `titulo_destaque`, `subtitulo`, `data_atualizacao`, `data_snapshot_fornecedores`, `inicio_base` (primeira data de pagamento), `ultimo_mes` (AAAA-MM), `metas` (`cobertura_min`, `fora_politica_max`, `kys_min`, `saldo_alerta`), `janela_vencimento_dias`, `base_percentual`, `rodape` |
| `dims` | Listas de rótulos; o código é a posição. `mes`, `gerencia`, `categoria`, `sub1`, `sub2`, `sub3`, `diretoria`, `fornecedor`, `contrato` (posição 0 = pagamentos sem contrato), `status`, `kys`, `risco`, `esteira` |
| `hierarquia` | `sub1`, `sub2`, `sub3`: para cada item, o código do nível de cima. Cada subcategoria é identificada pelo caminho completo, então nomes iguais em caminhos diferentes são itens diferentes |
| `fornecedores` | Arrays alinhados a `dims.fornecedor`: `raiz`, `kys` (código), `risco` (código) |
| `fato` | `n_linhas` + `colunas`: `mes`, `gerencia`, `categoria`, `sub1`, `sub2`, `sub3`, `diretoria`, `fornecedor`, `status`, `contrato`, opcional `enderecavel`, `valor` (float64), `n_pagamentos` (uint32). Cada coluna em lista JSON ou `{"dtype", "b64"}` little-endian |
| `contratos` | Arrays alinhados a `dims.contrato`: `descricao`, `fornecedor`, `data_inicio`, `data_fim`, `valor_contratado` (null se não informado), `esteira` (código), `n_aportes`, `valor_aportes`, `consumido`, `consumo_12m`, `inicio_antes_base` (0/1), `gerencia`, `categoria`, `sub1`, `sub2`, `sub3`, `diretoria` (códigos mais frequentes nos pagamentos; -1 se não houver). Mais: `anos` + `consumo_ano` (matriz contratos × anos em base64), `diretorias` (pares contrato, diretoria, valor, valor_12m em base64), `aportes` (listas contrato, data, valor) |

Ordens fixas: `status` = Com contrato, Baixo valor, Parcerias, Fora da Política, Não classificado · `kys` = Aprovado, Negado, Pendente, Sem informação · `risco` = Baixo, Médio, Alto, Sem avaliação · `esteira` = Não, Sim, Sem informação

## Desempenho medido

- 700 mil pagamentos → 273 mil linhas de fato (10,3 MB de HTML); incluir o contrato no grão acrescentou cerca de 4% de linhas
- Pipeline: cerca de 7 s
- Abertura: decodificação ~40 ms · cada mudança de filtro ou foco: 15 a 50 ms de cálculo + até 150 ms de desenho

Regras de edição do template: [04_template.md](04_template.md)
