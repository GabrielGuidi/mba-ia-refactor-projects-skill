# Template de relatório

Salvar em Markdown. Ordenar findings por severidade e, dentro dela, por impacto.

```md
# Relatório de Auditoria Arquitetural

## Projeto

- Nome: <nome>
- Stack: <linguagem, framework e banco>
- Arquivos analisados: <número>
- Linhas aproximadas: <número>
- Baseline: <resultado>

## Resumo

| Severidade | Total |
|---|---:|
| CRITICAL | <n> |
| HIGH | <n> |
| MEDIUM | <n> |
| LOW | <n> |
| **Total** | **<n>** |

## Findings

### [CRITICAL] <nome do problema>

- **Arquivo:** `path/to/file.ext:10-24`
- **Evidência:** <trecho ou comportamento objetivo, sem copiar blocos grandes>
- **Descrição:** <o que está errado>
- **Impacto:** <consequência concreta>
- **Recomendação:** <correção direta>

<!-- Repetir em ordem: CRITICAL, HIGH, MEDIUM, LOW. -->

## APIs e dependências deprecated

- <API, evidência, substituto e fonte da confirmação>
- Usar `Nenhuma confirmada` quando não houver evidência.

## Escopo recomendado para a Fase 3

- <mudanças ligadas aos findings>

## Validação planejada

- Instalação: `<comando>`
- Seed: `<comando ou não aplicável>`
- Boot: `<comando>`
- Testes: `<comandos>`
- Endpoints: `<método e caminho>`
```

Após exibir e salvar o relatório, perguntar:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Somente `y` autoriza alterações. Qualquer outra resposta encerra a execução após a Fase 2.
