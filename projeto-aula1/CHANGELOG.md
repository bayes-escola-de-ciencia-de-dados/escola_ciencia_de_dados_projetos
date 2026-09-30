# Histórico de versões

## Não publicado

- Painel clássico (`saida/painel_classico.html`): as 10 abas do painel anterior com período de 12 meses por padrão, filtro e aba de Contratos, aba Riscos (gauge de KYS aprovado, rosca do spend por KYS, tabela de fornecedores com risco) e Insights com sinais automáticos; sem Natureza e sem gráficos avançados
- Blocos compartilhados entre os templates e script `sincronizar_templates.py`, com teste que falha se divergirem
- Publicação no SharePoint: `saida/sharepoint/` com os dois painéis em .aspx lendo `dados.json`; atualizar dados passa a ser trocar só o JSON, com mensagem de carregamento e de erro
- Guia de evolução do projeto (docs/06_como_evoluir.md) e teste de documentação
- Contrato como filtro global e como lente, com ranking de contratos (spend, % consumido, saldo, vencimento, esteira expressa)
- Ficha do contrato: valor contratado, aportes, consumido, saldo, consumo 12 meses e por ano, diretorias pagadoras, lista de aportes e alertas de saldo
- Sinais de saldo de contrato no capítulo Onde agir
- Subcategorias vazias exibidas como Sem classificação, com contexto do nível de cima quando o nome se repete
- Eixos em R$ mi ou R$ mil conforme o tamanho dos valores
- Base de entrada: `aportes.csv` novo, `valor_contratado` obrigatório, `esteira_expressa` na tabela de contratos, pagamentos desde jan/2022
- Barra de abas mais compacta (botão Copiar link) e caixa de alerta com estilo próprio
- Contrato de dados v3.0 (quebra compatibilidade: a próxima versão publicada é a v3.0)

## v2.0-prototipo - 2026-09-27

- Painel reorganizado como história: página Onde olhar + 5 capítulos, com lentes Categoria, Diretoria e Fornecedor
- Cartões com pergunta e título-resposta calculado para o recorte
- Filtro Período: últimos 12 meses, YTD e anos fechados, com comparação de mesmo tamanho
- Navegação por abas ou rolagem (chave para teste com usuários) e link que reabre a visão exata
- Fornecedor pelo CNPJ raiz; grupo econômico removido
- Status contratual derivado (Com contrato, Baixo valor, Parcerias, Fora da Política, Não classificado)
- KYS e risco financeiro por fornecedor
- Nova base de entrada em 3 tabelas e pipeline `preparar_dados.py` + `gerar_painel.py`, com log em arquivo
- Testes das regras do pipeline
- Saem boxplot, histograma, heatmap, gauge, treemap e escala log

## v1.0 - 2026-09-25

- Template canônico aprovado, réplica do painel anterior com dados fictícios
- Contrato de dados colunar (dicionários + colunas base64) para suportar 700 mil linhas
- ECharts 5.6.0 embutido no HTML
