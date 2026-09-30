# 04 - Template HTML

`src/template/painel_template.html` é a fonte da verdade do painel: layout, estilo, gráficos e regras de cálculo. É um arquivo único, com CSS e JavaScript dentro, e só três marcadores que o pipeline substitui

`src/template/painel_classico.html` é o painel clássico de 10 abas ([decisão 0016](decisoes/0016-painel-classico.md)). Usa o mesmo JSON e os mesmos marcadores

| Marcador | Recebe |
|---|---|
| `/*__ECHARTS_LIB__*/` | `vendor/echarts.min.js` (ECharts 5.6.0) |
| `__SPEND_DATA__` | O JSON descrito em [03_contrato_de_dados.md](03_contrato_de_dados.md) (vazio no .aspx) |
| `__SPEND_URL__` | Vazio no HTML; no .aspx, o caminho do `dados.json` ([decisão 0017](decisoes/0017-dados-em-arquivo-no-sharepoint.md)) |

## Carregamento

O código do painel fica na função `painelApp()`. O carregador, no último `<script>`, decide como começar:

- Com dados embutidos (`data-url` vazio): chama `painelApp()` na hora
- Com `data-url`: mostra "Carregando dados...", busca o arquivo sem cache, coloca o texto no `<script id="spend-data">` e chama `painelApp()`. Se falhar, mostra o erro com o caminho buscado

## Mapa do arquivo

| Bloco | Onde | O que contém |
|---|---|---|
| Dicionário de cores | `:root` no início do `<style>` | Todas as cores. O JavaScript lê daqui |
| Estilos | restante do `<style>` | Cabeçalho, barra de abas, filtros, cartões, tabelas, selos |
| Estrutura HTML | `<body>` | Cabeçalho, barra fixa, filtros, bloco "Ver por / Foco", duas vistas vazias preenchidas pelo JS |
| 1. Estrutura fixa | `VISTAS`, `LENTES`, `FILTROS` | Abas, lentes e filtros do painel |
| 2. Tema | `C` | Cores lidas do CSS |
| 3. Dados | `decodificar`, `COL`, `CTR`, `CONTRATOS` | Leitura do JSON, das colunas binárias e dos atributos de contrato |
| 3. Contratos e rótulos | `totalCtr`, `saldoCtr`, `anosCtr`, `dirsCtr`, `aportesCtr`, `rotulo`, `contexto` | Saldo e histórico do contrato; nome de exibição com contexto do nível de cima |
| 4. Períodos | `opcoesPeriodo`, `faixa` | 12 meses, YTD, anos fechados e período de comparação |
| 5. Estado | `estado` | Filtros, período, lente, foco, vista, modo, escala da fonte |
| 6. Motor | `passar`, `cubo`, `aplicar` | Filtro em uma passada + agregações do recorte |
| 7. Formatação | `brl`, `pct`, `pp` | Números em pt-BR |
| 8. Gráficos | `barrasH`, `barra100`, `halteres`, `evolucao`, `colunasAno` | As formas visuais permitidas. Eixos escolhem R$ mi ou R$ mil pelo tamanho dos valores (`unidade`) |
| 9. Componentes | `kpi`, `cartao`, `tabela`, `meta` | Blocos de HTML reutilizáveis |
| 10. Vistas | `renderInicio`, `renderInicioContrato`, `fichaContrato`, `faixaContrato`, `cap1` a `cap5`, `sinais` | Conteúdo de cada aba; `contratoUnico()` decide quando a ficha aparece |
| 11. Navegação | `render`, `irPara`, `observarRolagem` | Abas e rolagem |
| 12. Controles | `dropdown`, `montarControles` | Filtros, período, lente e foco |
| 13. Link e fonte | `salvarHash`, `lerHash`, `definirEscala` | Link da visão e A-/A/A+ |
| 14. Inicialização | `iniciar` | Monta tudo ao abrir |

## Blocos compartilhados

O CSS e o JavaScript comuns aos dois templates ficam entre marcadores:

| Bloco | Marcadores | Contém |
|---|---|---|
| CSS | `/*__INICIO_CSS_COMPARTILHADO__*/` ... `/*__FIM_CSS_COMPARTILHADO__*/` | Cores, cabeçalho, filtros, cartões, tabelas, selos |
| JavaScript | `/*__INICIO_COMPARTILHADO__*/` ... `/*__FIM_COMPARTILHADO__*/` | Blocos 2 a 9b: tema, dados, períodos, estado, motor, formatação, gráficos, componentes, ficha do contrato, sinais, controles, link e fonte |
| Carregador | `/*__INICIO_CARREGADOR__*/` ... `/*__FIM_CARREGADOR__*/` | Dados embutidos ou busca do `dados.json` |

- Editar só no `painel_template.html` e rodar `python src/pipeline/sincronizar_templates.py`, que copia os blocos para o clássico
- `python src/pipeline/sincronizar_templates.py --verificar` só confere, sem alterar
- `FILTROS` fica fora dos blocos, mas precisa ser igual nos dois (o teste confere)
- O que é só do clássico fica depois dos blocos: bloco 10 (gráficos `colunasComparadas`, `barrasDiv`, `linhaPct`, `gauge`, `rosca`), bloco 11 (uma função `vNome` por aba) e blocos 12 e 13 (navegação, controles e inicialização)

## Regras de edição

- Cor nova ou ajuste de cor: só no dicionário `:root`
- Gráfico novo: usar um dos helpers do bloco 8. Não criar estilo avulso de ECharts
- Todo cartão tem `pergunta` (a dúvida do usuário) e `titulo` (a resposta calculada). Se o dado não sustenta a frase, usar um título neutro
- Todo eixo tem unidade (R$ mi, % do gasto) e todo tamanho de fonte de gráfico passa por `fs(n)`, para respeitar o A-/A/A+
- Status, KYS, risco e esteira têm ordem fixa (ver contrato de dados). Não reordenar
- Nome exibido de subcategoria ou contrato sempre por `rotulo(chave, codigo)`, nunca direto de `DIMS`
- Detalhes de um único contrato (aportes, consumo por ano, diretorias do contrato) só aparecem na ficha, quando `contratoUnico()` não é nulo; listas de contratos podem mostrar saldo e % consumido por linha
- Não alterar os três marcadores
- Toda mudança de layout entra no [CHANGELOG](../CHANGELOG.md), e mudança de regra vira um registro em [decisoes/](decisoes/)

## Como fazer mudanças comuns

**Adicionar um cartão a um capítulo**
1. Calcular o que precisa dentro da função do capítulo (`cap1` a `cap5`), a partir de `estado.his`
2. Se o dado ainda não existe no cubo, acrescentar o acumulador em `cubo()`
3. Incluir `cartao({ id, pergunta, titulo, desc })` no HTML retornado e registrar o desenho com `fila.push(() => barrasH(id, itens))`

**Adicionar um filtro**
1. Acrescentar a coluna no pipeline (fato + `dims`) e no contrato de dados
2. Incluir em `FILTROS` e, se entrar no motor de disponibilidade, em `DIMS_DISP`

**Mudar metas**
- As metas vêm do JSON (`meta.metas`), definidas em `preparar_dados.py`. O template não tem números fixos de meta

## Como verificar

1. `python src/pipeline/gerar_painel.py --base exemplos/base_exemplo --data-atualizacao 2026-09-15`
2. Abrir `saida/painel.html` e percorrer: Onde olhar, 5 capítulos nas 3 lentes, modos Abas e Rolagem, A+ e Copiar link
3. Abrir `saida/painel_classico.html` e percorrer as 10 abas, com e sem filtro de categoria e de contrato
4. Modo arquivo: em `saida/sharepoint/`, rodar `python -m http.server`, copiar um .aspx para .html e abrir em `http://localhost:8000/` (o navegador não abre .aspx direto do disco)
5. Console do navegador (F12) sem erros; os painéis registram ali o tempo de cálculo e de desenho
