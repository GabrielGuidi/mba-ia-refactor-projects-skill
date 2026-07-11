---
name: refactor-arch
description: Analisar, auditar e refatorar projetos backend para uma arquitetura MVC segura e testável. Usar quando for necessário detectar stack e arquitetura, localizar anti-patterns com arquivo e linha, gerar relatório por severidade, migrar Python/Flask, Node.js/Express ou outra stack para MVC e validar que endpoints continuam funcionando.
---

# Refatorar arquitetura

Executar as fases em ordem. Não modificar arquivos durante as fases 1 e 2.

## Referências

Ler cada referência no início da fase indicada:

- Fase 1: [project-analysis.md](references/project-analysis.md).
- Fase 2: [anti-pattern-catalog.md](references/anti-pattern-catalog.md) e [audit-report-template.md](references/audit-report-template.md).
- Fase 3: [mvc-guidelines.md](references/mvc-guidelines.md) e [refactoring-playbook.md](references/refactoring-playbook.md).

## Fase 1: análise

1. Identificar raiz, linguagem, framework, dependências, banco e comandos de execução.
2. Mapear domínio, endpoints, tabelas, arquivos fonte e arquitetura atual.
3. Ignorar dependências instaladas, builds, caches, ambientes virtuais e arquivos gerados.
4. Executar o baseline quando for seguro: instalar dependências declaradas, popular banco quando necessário, iniciar aplicação e testar endpoints representativos.
5. Registrar comandos e respostas do baseline para repetir após a refatoração.
6. Imprimir o resumo no formato definido em `project-analysis.md`.

## Fase 2: auditoria

1. Ler todo arquivo fonte relevante antes de concluir a auditoria.
2. Cruzar evidências com o catálogo. Não inferir finding sem evidência no código ou em ferramenta de diagnóstico.
3. Informar arquivo e linha exatos. Usar intervalo para função ou classe inteira.
4. Ordenar findings por `CRITICAL`, `HIGH`, `MEDIUM` e `LOW`.
5. Gerar pelo menos 5 findings, incluindo 1 `CRITICAL` ou `HIGH`, quando houver evidência real.
6. Salvar o relatório no caminho solicitado. Se não houver caminho, usar `reports/audit-<project>.md` na raiz do repositório.
7. Mostrar o relatório e perguntar exatamente:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

8. Encerrar sem modificar código se a resposta não for `y`.

## Fase 3: refatoração

Executar somente após confirmação explícita com `y`.

1. Preservar endpoints, formatos de resposta e comandos públicos.
2. Escolher a menor estrutura MVC que resolva os findings confirmados.
3. Aplicar primeiro correções de segurança e integridade.
4. Separar configuração, models, controllers, routes/views e middleware de erros.
5. Reutilizar estrutura válida que já exista. Não mover arquivos apenas por estética.
6. Atualizar APIs deprecated encontradas.
7. Remover código substituído e imports sem uso.
8. Repetir instalação, seed, boot e testes de endpoints do baseline.
9. Executar testes existentes. Não ocultar falhas.
10. Reauditar os findings originais e registrar os que foram corrigidos ou permaneceram.
11. Imprimir a estrutura final e o resultado de cada validação.

## Restrições

- Não alterar contratos HTTP sem necessidade de segurança explicitamente registrada.
- Não adicionar framework, ORM ou biblioteca se a stack atual resolver o problema.
- Não inventar testes aprovados. Informar comando, resultado e limite da validação.
- Não declarar zero anti-patterns sem executar nova auditoria.
- Não apagar dados ou arquivos do usuário sem autorização.
