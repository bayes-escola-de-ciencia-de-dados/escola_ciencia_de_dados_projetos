# 01 - Especificação do painel

O que o painel mostra, para quem e por quê. Detalhes de cada decisão em [decisoes/](decisoes/)

## Público e uso

- Compradores, gerentes de compras e executivos de compras
- Acesso por link; e-mails periódicos com insights levam o link já filtrado (botão "Copiar link")
- Objetivos: conhecer as próprias categorias, apoiar a redistribuição de share e montar estratégias de negociação
- A base não tem preço unitário nem quantidade: nada no painel compara preços

## Princípios

- O painel guia o usuário por uma história, sempre na mesma ordem
- Cada gráfico responde a uma pergunta. Acima do título aparece a pergunta; o título é a resposta, calculada para o recorte
- Só 6 formas visuais: card de número, barras horizontais ordenadas, colunas mensais, barra 100%, halteres e tabela com selos
- Fornecedor = CNPJ raiz (8 dígitos). Grupo econômico não aparece no painel
- Todo cálculo usa `data_pagamento`. A data de atualização da base só aparece no cabeçalho

## Estrutura

**Lente + foco** (escolha principal): Categoria, Diretoria, Fornecedor ou Contrato, com foco em um item ou em todos

**Filtros globais** (continuam existindo): Período, Gerência Compras, Categoria, Subcategoria 1, Subcategoria 2, Subcategoria 3, Diretoria, Contrato
- Quando a lente é Categoria, Diretoria ou Contrato e há foco, o filtro correspondente fica travado mostrando o foco
- Níveis de subcategoria vazios aparecem como "Sem classificação"; quando um nome se repete, o filtro mostra o nível de cima como contexto
- O filtro Contrato busca por número, descrição ou fornecedor e tem a opção "(pagamentos sem contrato)"

**Período**

| Opção | Compara com |
|---|---|
| Últimos 12 meses (padrão) | 12 meses anteriores |
| YTD do ano vigente | Mesmo período do ano anterior |
| Anos fechados | Ano anterior |

A janela termina no último mês com pagamentos na base

**Navegação**: abas ou rolagem (chave no topo, para teste com usuários). As mesmas abas funcionam como índice no modo rolagem

## Vistas

| Vista | Conteúdo |
|---|---|
| Onde olhar | Ranking da lente com spend, variação, share, % Fora da Política, contratos vencendo em 90 dias e spend em fornecedores de risco. Clique abre a história. Na lente Contrato: spend, variação, % consumido, saldo, vencimento e esteira expressa, com KPI de spend via esteira expressa |
| Ficha do contrato | Aparece no topo da história quando há exatamente um contrato no recorte (foco da lente ou filtro com um contrato). Ver seção própria |
| 1. Quanto gastamos | Spend, variação, fornecedores, pagamentos · colunas mensais com período atual e de comparação · composição (categorias ou subcategorias) · diretorias que consomem |
| 2. Com quem | Fornecedores e share (fornecedor ou contrato único em foco: diretorias que pagam) · halteres de mudança de share · subcategorias com fornecedor único |
| 3. Com que proteção | Cobertura, Fora da Política, contratos vencendo · situação contratual em barra 100% · Fora da Política por área · fornecedores sem contrato · contratos vencendo em 180 dias |
| 4. Com que risco | % fornecedores com KYS aprovado, spend com KYS negado, spend em risco alto · distribuição por risco · fornecedores de atenção (lente Fornecedor com foco: selos de KYS e risco) |
| 5. Onde agir | Lista de sinais ordenada por R$: vencimento, Fora da Política, KYS negado, risco alto, fornecedor único, saldo de contrato (saldo abaixo de 10%, estourado ou no ritmo de acabar antes do vencimento) |

## Metas

| Indicador | Meta |
|---|---|
| Cobertura contratual (com contrato ÷ spend total) | ≥ 80% |
| Fora da Política (÷ spend total) | ≤ 10% |
| Fornecedores com KYS aprovado (% dos fornecedores com pagamento no período) | ≥ 95% |
| Risco financeiro | Sem meta, só distribuição |
| Saldo de contrato (saldo ÷ contratado + aportes) | Alerta abaixo de 10% |

Denominador: spend total na v1. Quando a base trouxer `enderecavel`, o painel passa a usar o spend endereçável automaticamente

## Ficha do contrato

Visão total do contrato, independente dos filtros. Só aparece com um único contrato no recorte; nas demais abas (modo abas) vira uma faixa-resumo

- Fornecedor, descrição, vigência, esteira expressa (Sim/Não) e prazo até o vencimento
- Valor contratado · aportes (quantidade e valor) · consumido · saldo · consumo dos últimos 12 meses
- Saldo = valor contratado + aportes - consumido
- Consumido = pagamentos desde o início da base (jan/2022). Contrato iniciado antes disso recebe o aviso de consumo parcial
- Barra consumido vs saldo (ou excedente, quando estourado) · consumo por ano · diretorias que pagam (últimos 12 meses) · lista de aportes
- Alerta quando o consumo passou do contratado ou quando, no ritmo dos últimos 12 meses, o saldo acaba antes do vencimento

## Painel clássico

Mesmos dados, filtros e períodos do painel em história, no formato de abas que os usuários já conhecem ([decisão 0016](decisoes/0016-painel-classico.md)). Período padrão: últimos 12 meses

| Aba | Mostra |
|---|---|
| Executivo | Indicadores do período, evolução mensal, situação contratual, top 10 fornecedores e categorias |
| Tendências | Mês a mês contra o período anterior, categorias e fornecedores que mais cresceram e caíram, fornecedores novos |
| Fornecedores | Top 15, mudança de share dos 10 maiores e tabela de fornecedores |
| Categorias | Spend por categoria e subcategoria, fragmentação de fornecedores e subcategorias de fornecedor único |
| Pareto & Concentração | Top 20 acumulado e concentração por categoria |
| Com / Sem Contrato | Situação contratual, trajetória de Fora da Política, Fora da Política por categoria e diretoria, fornecedores sem contrato e vencimentos |
| Contratos | Ranking de contratos; o clique abre a ficha do contrato |
| Riscos | Gauge com ponteiro do % de fornecedores com KYS aprovado (meta 95%), rosca do spend por situação de KYS e tabela de fornecedores com KYS negado ou risco financeiro médio/alto, do recorte filtrado |
| Insights | Sinais automáticos, os mesmos do capítulo Onde agir |
| Glossário | Termos e regras de cálculo |

Fora do clássico: aba Natureza, boxplot, histograma, heatmap, treemap e escala log

## Status contratual (derivado pelo pipeline)

- `id_contrato` preenchido → Com contrato
- Vazio → `classificacao_sem_contrato`: Baixo valor, Parcerias (permitidos) ou Fora da Política
- Nenhum dos dois → Não classificado (aparece como nota de qualidade de dado)

## Inventário de perguntas

| # | Pergunta | Onde |
|---|---|---|
| P01 | Qual o spend no período (padrão: 12 meses)? | Cap. 1 |
| P02 | Como o gasto evoluiu? | Cap. 1 |
| P03 | Em quais categorias/subcategorias está o dinheiro? | Cap. 1 |
| P04 | Quanto cada diretoria gasta? | Cap. 1 e Onde olhar (lente Diretoria) |
| P05 | Quem são os fornecedores e qual o share? | Cap. 2 |
| P06 | Há concentração ou fornecedor único? | Cap. 2 |
| P07 | Como o share mudou? | Cap. 2 |
| P08 | Com quais fornecedores uma diretoria gasta? | Cap. 2, lente Diretoria |
| P09 | Quais diretorias um fornecedor atende? | Cap. 2, lente Fornecedor |
| P10 | Quanto está coberto por contrato? | Cap. 3 |
| P11 | Quanto está Fora da Política, com quem e onde? | Cap. 3 |
| P12 | Quais fornecedores recebem sem contrato? | Cap. 3 |
| P13 | Quais contratos vencem em breve? | Cap. 3 |
| P14 | Quanto pagamos a fornecedores com KYS negado? | Cap. 4 |
| P15 | Como o spend se distribui por risco financeiro? | Cap. 4 |
| P16 | Onde agir primeiro? | Cap. 5 |
| P17 | O que pede atenção? | Onde olhar |
| P18 | Como foi o consumo do contrato nos últimos 12 meses? | Ficha do contrato |
| P19 | Como foi o consumo do contrato em cada ano? | Ficha do contrato |
| P20 | Quanto do contrato já foi consumido e qual o saldo? | Ficha do contrato |
| P21 | Quais áreas pagam o contrato? | Ficha do contrato |
| P22 | Quem é o fornecedor do contrato? | Ficha do contrato |
| P23 | Quantos aportes o contrato recebeu? | Ficha do contrato |
| P24 | O contrato foi negociado pela esteira expressa? | Ficha do contrato e Onde olhar (lente Contrato) |
| P25 | Quais contratos recebem mais pagamentos? (antiga F01) | Onde olhar, lente Contrato |

## Backlog

Perguntas registradas para versões futuras: [backlog.md](backlog.md)

## Em aberto

- Abas ou rolagem: decidir após teste com usuários
- Status extras de KYS (Pendente?) e de risco (Sem avaliação?): o pipeline já aceita os dois
