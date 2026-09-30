# 0003 - Dados colunares e agregados no grão dos filtros

- **Data**: 2026-09-25
- **Contexto**: O painel anterior ficava lento nos filtros; a base pode ter 700 mil pagamentos
- **Decisão**: Pipeline agrega no grão mês x gerência x subcategoria 3 x diretoria x fornecedor x status; colunas codificadas em dicionário e binário; filtro aplicado só ao clicar em Aplicar
- **Consequências**: 700 mil pagamentos viram cerca de 260 mil linhas; cada filtro leva menos de 0,1 s
