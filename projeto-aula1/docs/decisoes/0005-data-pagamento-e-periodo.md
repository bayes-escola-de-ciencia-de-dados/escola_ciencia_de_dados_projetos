# 0005 - Cálculos por data de pagamento e filtro Período

- **Data**: 2026-09-27
- **Contexto**: Era preciso ver 12 meses móveis, o ano vigente e anos fechados
- **Decisão**: Todo cálculo usa data_pagamento; Período oferece Últimos 12 meses (padrão), YTD e anos fechados; a comparação usa o período anterior de mesmo tamanho; a data de atualização só aparece no cabeçalho; prazo de contrato conta a partir do dia em que o painel é aberto
- **Consequências**: A janela termina no último mês com pagamentos
