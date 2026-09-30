# 0013 - Grão pelo caminho da subcategoria, não pela categoria

- **Data**: 2026-09-28
- **Contexto**: Foi proposto usar a categoria no grão do fato, já que a subcategoria 3 nem sempre existe
- **Decisão**: Manter o caminho completo da subcategoria no grão: ele é o nível mais profundo que existe em cada pagamento e sustenta os filtros Subcategoria 1, 2 e 3, a composição por subcategoria e o alerta de fornecedor único. Subir para a categoria reduziria 36% das linhas, mas desligaria essas visões
- **Consequências**: Os filtros de subcategoria continuam funcionando
