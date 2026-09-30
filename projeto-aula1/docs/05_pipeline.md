# 05 - Pipeline

Estrutura lógica de cada script, para confrontar o código com o que ele deveria fazer. Todos gravam log em `saida/logs/AAAAMMDD_HHMMSS_<script>.log`

## Fluxo

```
dados/entrada/*.csv -> preparar_dados.py -> JSON -> injetar_painel.py -> saida/painel.html
                                                                      -> saida/painel_classico.html
                                                                      -> saida/sharepoint/ (painel.aspx, painel_classico.aspx, dados.json)
                       \_____________ gerar_painel.py (roda tudo) _______________/
```

## comum.py

- `RAIZ`: pasta raiz do repositório
- `configurar_log(nome)`: log no terminal e em arquivo com data e hora

## preparar_dados.py

```
ler pagamentos, fornecedores, contratos e aportes (CSV ; e decimal ,); sem aportes.csv = nenhum aporte

cadastro de fornecedores:
    raiz = 8 primeiros dígitos do CNPJ
    nome = nome da filial 0001 (matriz), senão o primeiro
    kys e risco = pior status entre os CNPJs da raiz
    snapshot = maior data_snapshot

pagamentos:
    raiz = 8 primeiros dígitos do CNPJ
    se raiz não está no cadastro: cria "CNPJ <raiz>" com KYS "Sem informação" e avisa no log
    status = "Com contrato" se id_contrato preenchido
             senão classificacao_sem_contrato se for Baixo valor, Parcerias ou Fora da Política
             senão "Não classificado"
    mes = AAAA-MM de data_pagamento
    ultimo_mes = maior mes; inicio_base = menor data_pagamento
    subcategoria vazia = "Sem classificação" (quantidade no log)

dicionários (dims): lista ordenada de rótulos por dimensão; código = posição
    hierarquia categoria > sub1 > sub2 > sub3 codificada pelo caminho completo
    hierarquia: para cada sub1, sub2 e sub3, o código do nível de cima
    contrato: posição 0 = pagamentos sem contrato; depois os ids em ordem

fato = soma de valor e contagem de pagamentos agrupados por
       mes, gerencia, categoria, sub1, sub2, sub3, diretoria, fornecedor, status, contrato (+ enderecavel se existir)
    colunas gravadas em binário base64 com o menor tipo inteiro que cabe

contratos (arrays alinhados a dims.contrato):
    entram os que têm pagamento + os cadastrados com data_fim >= data_atualizacao - 60 dias
    consumido = soma de todos os pagamentos do contrato na base
    consumo_12m = soma dos pagamentos nos 12 meses até ultimo_mes
    consumo_ano = soma por ano (matriz contratos x anos)
    n_aportes e valor_aportes = contagem e soma em aportes.csv
    esteira = Sim 1, Não 0, outro 2
    inicio_antes_base = data_inicio < inicio_base
    fornecedor = raiz do cadastro do contrato (senão o mais frequente nos pagamentos)
    categoria, subcategorias, gerência e diretoria = valor mais frequente nos pagamentos do contrato
    diretorias = pares (contrato, diretoria, valor total, valor 12 meses)

meta: títulos, datas, inicio_base, ultimo_mes, metas (80%, 10%, 95%, saldo 10%), janela de 180 dias, base do percentual
gravar JSON
```

## injetar_painel.py

```
validar: blocos obrigatórios presentes; colunas em lista com n_linhas
ler template; exigir cada marcador exatamente 1 vez
escapar "</script" na biblioteca
modo embutido (HTML): JSON no marcador de dados, com "</" escapado; url vazia
modo arquivo (.aspx, com url_dados): marcador de dados vazio; url_dados no atributo data-url
gravar
```

## gerar_painel.py

```
preparar(base, data_atualizacao) -> validar -> gravar JSON ao lado do HTML
gravar dados.json em saida/sharepoint/
para cada template (painel_template -> painel, painel_classico -> painel_classico):
    injetar embutido em saida/<nome>.html
    injetar em modo arquivo em saida/sharepoint/<nome>.aspx, apontando para --url-dados (padrão dados.json)
```

## sincronizar_templates.py

```
para cada bloco compartilhado (CSS e JavaScript):
    copiar o trecho entre os marcadores do painel_template.html para o painel_classico.html (CSS, JavaScript e carregador)
--verificar: não grava; sai com erro se algum bloco diferir
```

## exemplos/gerar_base_exemplo.py

Gera os 3 CSVs fictícios no formato de [02_base_de_entrada.md](02_base_de_entrada.md). Parâmetros: `--pagamentos` (padrão 30 mil), `--seed`, `--saida`

## Testes

`python -m pytest tests` cobre as regras do pipeline (`test_preparar_dados.py`): CNPJ raiz, status derivado, pior status por raiz, nome da matriz, soma de valores preservada, fornecedor fora do cadastro, período, contrato no fato, atributos e saldo do contrato, aportes opcionais, contrato anterior à base e nível vazio

A sincronia entre código e documentação é checada em `test_documentacao.py` (ver [06](06_como_evoluir.md))
