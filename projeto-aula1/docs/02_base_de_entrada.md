# 02 - Base de entrada

Quatro arquivos CSV (separador `;`, decimal `,`, UTF-8), com pagamentos desde jan/2022. O `preparar_dados.py` lê esta pasta e gera o arquivo do painel. Os CSVs em `exemplos/base_exemplo/` mostram o formato na prática

## pagamentos.csv - uma linha por pagamento

| Campo | Tipo | Obrigatório | Observação |
|---|---|---|---|
| `data_pagamento` | AAAA-MM-DD | Sim | Base de todo cálculo de período |
| `valor_bruto` | decimal | Sim | R$ nominal |
| `cnpj_fornecedor` | texto (14 dígitos) | Sim | O pipeline agrupa pela raiz (8 primeiros dígitos) |
| `categoria` | texto | Sim | |
| `subcategoria_1`, `subcategoria_2`, `subcategoria_3` | texto | Sim (vazio quando o nível não existe) | Nível vazio aparece como "Sem classificação". Deixar o campo realmente vazio, sem textos como "N/A" |
| `gerencia_compras` | texto | Sim | |
| `diretoria` | texto | Sim | |
| `id_contrato` | texto | Sim (vazio quando não há contrato) | Preenchido = Com contrato |
| `classificacao_sem_contrato` | texto | Sim quando `id_contrato` vazio | Baixo valor · Parcerias · Fora da Política |
| `enderecavel` | sim/não | Futuro (F08) | Se existir, vira o denominador de cobertura e Fora da Política |
| `tipo_compra` | texto | Futuro (F03) | PR/SPOT |

## fornecedores.csv - uma linha por CNPJ, snapshot atual

| Campo | Tipo | Obrigatório | Observação |
|---|---|---|---|
| `cnpj_fornecedor` | texto (14 dígitos) | Sim | |
| `nome_fornecedor` | texto | Sim | O painel usa o nome da matriz (filial 0001) |
| `status_kys` | texto | Sim | Aprovado · Negado (aceita Pendente e Sem informação) |
| `risco_financeiro` | texto | Sim | Baixo · Médio · Alto (aceita Sem avaliação) |
| `data_snapshot` | AAAA-MM-DD | Sim | Aparece como "posição de dd/mm/aaaa" |

Se CNPJs da mesma raiz tiverem status diferentes, vale o pior (Negado > Pendente > Sem informação > Aprovado; Alto > Médio > Sem avaliação > Baixo)

## contratos.csv - uma linha por contrato

| Campo | Tipo | Obrigatório | Observação |
|---|---|---|---|
| `id_contrato` | texto | Sim | Mesma chave dos pagamentos |
| `descricao` | texto | Sim | |
| `cnpj_fornecedor` | texto | Sim | |
| `data_inicio`, `data_fim` | AAAA-MM-DD | Sim | Vencimento = `data_fim` |
| `valor_contratado` | decimal | Sim | Valor original, sem aportes. Sem ele o painel não calcula saldo |
| `esteira_expressa` | Sim/Não | Sim | Contrato negociado pela esteira expressa (CSC) |

## aportes.csv - uma linha por aporte (aditivo de valor)

| Campo | Tipo | Obrigatório | Observação |
|---|---|---|---|
| `id_contrato` | texto | Sim | Mesma chave dos contratos |
| `data_aporte` | AAAA-MM-DD | Sim | |
| `valor_aporte` | decimal | Sim | Valor acrescentado ao contrato |

Se o arquivo não existir, o pipeline segue considerando que nenhum contrato recebeu aporte (e avisa no log)

## Regras aplicadas pelo pipeline

- Status contratual derivado de `id_contrato` + `classificacao_sem_contrato` (vazio nos dois = Não classificado)
- Pagamento com CNPJ fora do cadastro entra como "CNPJ xxxxxxxx", com KYS "Sem informação" e é registrado no log
- Contrato herda categoria, subcategorias, gerência e diretoria mais frequentes nos seus pagamentos
- Consumido = todos os pagamentos na base com aquele `id_contrato`; consumo 12 meses = pagamentos dos últimos 12 meses
- Saldo = `valor_contratado` + soma dos aportes - consumido
- Contrato iniciado antes da primeira data da base recebe o aviso de consumo parcial
- Níveis de subcategoria vazios viram "Sem classificação"; a quantidade vai para o log
- Contrato com pagamento e sem cadastro aparece como "Contrato sem cadastro" e é registrado no log
- São exportados os contratos com pagamento e os demais que vencem a partir de 60 dias antes da data de atualização

## Como rodar

```
python src/pipeline/gerar_painel.py --base dados/entrada --data-atualizacao AAAA-MM-DD
```

Os 4 CSVs reais ficam em `dados/entrada/`, pasta que o git ignora
