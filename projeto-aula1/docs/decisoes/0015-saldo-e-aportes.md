# 0015 - Saldo com aportes e consumo desde o início da base

- **Data**: 2026-09-28
- **Contexto**: Aporte é um aditivo que aumenta o valor do contrato; a base de pagamentos começa em 2022
- **Decisão**: Saldo = valor contratado + aportes - pagamentos na base; aportes em arquivo próprio (aportes.csv); contratos iniciados antes da base mostram aviso de consumo parcial; alerta de saldo abaixo de 10%, de consumo acima do contratado e de saldo que acaba antes do vencimento no ritmo dos últimos 12 meses
- **Consequências**: valor_contratado passa a ser obrigatório; esteira_expressa entra na tabela de contratos
