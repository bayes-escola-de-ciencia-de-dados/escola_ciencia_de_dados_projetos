# 0002 - Template HTML único e canônico

- **Data**: 2026-09-25
- **Contexto**: Gerar o HTML por script fazia o layout variar entre atualizações
- **Decisão**: Um template HTML fixo é a fonte da verdade; o pipeline só injeta dados por dois marcadores; ECharts 5.6.0 embutido para funcionar sem internet
- **Consequências**: Layout determinístico; mudança visual só no template
