# 0014 - Subcategorias vazias como Sem classificação

- **Data**: 2026-09-28
- **Contexto**: A base traz subcategorias ausentes em formatos variados; repetir a categoria no nível vazio criaria falsas subcategorias
- **Decisão**: A base entrega o nível ausente vazio; o pipeline exibe Sem classificação; nomes repetidos em caminhos diferentes mostram o nível de cima como contexto nos filtros e gráficos
- **Consequências**: Arquivo menor; nenhum nome inventado nos filtros; quantidade de vazios registrada no log
