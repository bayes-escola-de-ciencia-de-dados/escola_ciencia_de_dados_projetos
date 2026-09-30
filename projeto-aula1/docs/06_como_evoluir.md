# 06 - Como evoluir o projeto

Regra central: código e documentação entram no mesmo commit. Mudança sem documentação atualizada não está pronta

## Tipo de mudança → o que atualizar

| Mudança | Atualizar |
|---|---|
| Ajuste visual (cor, texto, posição, estilo de gráfico) | Template + CHANGELOG |
| Novo cartão, pergunta ou capítulo | Template + inventário de perguntas em [01](01_especificacao.md) + CHANGELOG; se veio do backlog, remover de lá |
| Nova coluna na base | [02](02_base_de_entrada.md) + pipeline + [05](05_pipeline.md) + teste; se chegar ao painel, também [03](03_contrato_de_dados.md) |
| Mudança de regra (meta, status, período, cálculo) | Nova decisão em [decisoes/](decisoes/README.md) + [01](01_especificacao.md) + código + teste + CHANGELOG |
| Mudança na estrutura do template (novo helper, novo bloco) | [04](04_template.md) |
| Mudança em bloco compartilhado (motor, gráficos, componentes) | Editar no `painel_template.html`, rodar `sincronizar_templates.py` e conferir os dois painéis |
| Ideia ou pergunta nova, ainda sem data | Só o [backlog](backlog.md) |
| Correção de erro | CHANGELOG + teste que reproduz o erro, quando for no pipeline |

## Versões

- Cada commit acrescenta uma linha na seção **Não publicado** do [CHANGELOG](../CHANGELOG.md)
- Ao liberar para os usuários, a seção vira `vX.Y` com a data, e o commit recebe a tag: `git tag -a vX.Y -m "resumo"`
- `Y` sobe a cada entrega; `X` sobe só quando a base de entrada ou o contrato de dados mudam de forma incompatível (quando a base real precisa ser ajustada). Nesse caso, a versão do contrato em `preparar_dados.py` e em [03](03_contrato_de_dados.md) também sobe
- A cada versão publicada: reler [01](01_especificacao.md) e o [backlog](backlog.md) para ver se ainda refletem o painel

## Decisões

- Uma decisão por arquivo em `docs/decisoes/`, numerada em sequência: `NNNN-titulo-curto.md`
- Campos: Data, Contexto, Decisão, Consequências
- Decisão não se apaga nem se reescreve: para mudar, criar uma nova que cite a antiga ("Substitui a 0007") e acrescentar "Substituída pela NNNN" na antiga
- Toda decisão nova entra no índice [decisoes/README.md](decisoes/README.md)

## Checklist antes de cada commit

1. Os dois painéis geram sem erro: `python src/pipeline/gerar_painel.py --base exemplos/base_exemplo`
2. Os testes passam: `python -m pytest tests`
3. A tabela acima foi seguida para o tipo de mudança
4. A linha no CHANGELOG está em Não publicado
5. A mensagem do commit diz o que mudou e por quê

## Trava automática

`tests/test_documentacao.py` falha quando:

- a versão do contrato em [03](03_contrato_de_dados.md) difere da versão gerada por `preparar_dados.py`
- existe decisão fora do índice
- algum link entre documentos está quebrado
- algum filtro do template não aparece na especificação
- os marcadores de algum template não aparecem exatamente uma vez
- os blocos compartilhados ou os filtros diferem entre os dois templates
- o CHANGELOG não começa pela seção Não publicado

O teste pega esquecimentos, não garante que o texto esteja certo. A revisão continua sendo humana
