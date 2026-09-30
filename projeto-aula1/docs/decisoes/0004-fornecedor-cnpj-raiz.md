# 0004 - Fornecedor pelo CNPJ raiz, sem grupo econômico

- **Data**: 2026-09-27
- **Contexto**: Compradores não reconhecem grupo econômico; a visão deles é sempre o fornecedor
- **Decisão**: Fornecedor = 8 primeiros dígitos do CNPJ, com o nome da matriz; KYS e risco da raiz = pior status entre os CNPJs
- **Consequências**: Grupo econômico sai do painel, da base e dos textos
