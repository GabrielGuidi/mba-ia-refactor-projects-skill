# Relatório de Auditoria Arquitetural

## Projeto

- Nome: `ecommerce-api-legacy`
- Stack: Node.js, Express 4.18.2 e SQLite3 5.1.6
- Arquivos analisados: 3
- Linhas aproximadas: 180
- Baseline: PASS. Aplicação iniciou; relatório financeiro e checkout responderam HTTP 200.

## Resumo

| Severidade | Total |
|---|---:|
| CRITICAL | 3 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **10** |

## Findings

### [CRITICAL] Secrets de produção hardcoded

- **Arquivo:** `src/utils.js:1-7`
- **Evidência:** credenciais de banco e uma chave live do gateway estão em `config`.
- **Descrição:** secrets reais ou realistas estão versionados com o código.
- **Impacto:** permite comprometer banco, pagamento e serviços associados.
- **Recomendação:** revogar os valores e carregar novas credenciais por variáveis de ambiente.

### [CRITICAL] Cartão e chave de pagamento registrados no log

- **Arquivo:** `src/AppManager.js:28-46`
- **Evidência:** `console.log` imprime `cc` e `config.paymentGatewayKey` durante o checkout.
- **Descrição:** dados financeiros sensíveis são enviados ao log da aplicação.
- **Impacto:** expõe cartão e credencial de pagamento a operadores e sistemas de log.
- **Recomendação:** remover o log sensível e registrar apenas identificadores seguros da transação.

### [CRITICAL] Senhas armazenadas com proteção reversível

- **Arquivo:** `src/AppManager.js:18`, `src/AppManager.js:66-72`, `src/utils.js:17-23`
- **Evidência:** a seed usa texto puro e `badCrypto` repete Base64 sem salt.
- **Descrição:** Base64 não é função de hash de senha e o resultado é previsível.
- **Impacto:** credenciais podem ser recuperadas após acesso ao banco.
- **Recomendação:** usar `crypto.scrypt` com salt aleatório e migrar registros existentes.

### [HIGH] God Class concentra toda a aplicação

- **Arquivo:** `src/AppManager.js:4-141`
- **Evidência:** a classe cria banco, seed, rotas, checkout, relatório e exclusão de usuário.
- **Descrição:** HTTP, domínio e persistência estão acoplados em uma única classe.
- **Impacto:** dificulta testes, manutenção e isolamento de falhas.
- **Recomendação:** separar routes, controllers, models e services por responsabilidade.

### [HIGH] Rotas administrativas e destrutivas sem autorização

- **Arquivo:** `src/AppManager.js:80-137`
- **Evidência:** relatório financeiro e exclusão de usuário não verificam identidade ou role.
- **Descrição:** qualquer cliente pode acessar dados financeiros ou excluir usuários.
- **Impacto:** causa exposição de dados e perda não autorizada.
- **Recomendação:** exigir autenticação e autorização administrativa verificável.

### [MEDIUM] Checkout sem transação atômica

- **Arquivo:** `src/AppManager.js:43-63`
- **Evidência:** matrícula, pagamento e auditoria são gravados por callbacks separados.
- **Descrição:** não há `BEGIN`, `COMMIT` e `ROLLBACK` envolvendo o caso de uso.
- **Impacto:** falhas intermediárias deixam registros incompletos.
- **Recomendação:** executar o fluxo em uma única transação.

### [MEDIUM] Consultas N+1 no relatório financeiro

- **Arquivo:** `src/AppManager.js:80-128`
- **Evidência:** cada curso consulta matrículas; cada matrícula consulta usuário e pagamento.
- **Descrição:** o volume de queries cresce com cursos e matrículas.
- **Impacto:** aumenta latência e complexidade assíncrona.
- **Recomendação:** usar JOIN e agregação no SQLite.

### [MEDIUM] Erros ignorados e integridade referencial quebrada

- **Arquivo:** `src/AppManager.js:57-61`, `src/AppManager.js:92-126`, `src/AppManager.js:131-136`
- **Evidência:** callbacks usam dados sem tratar `err`; exclusão deixa matrículas e pagamentos órfãos.
- **Descrição:** falhas de banco podem continuar o fluxo e exclusões não preservam relações.
- **Impacto:** respostas incorretas, exceções e dados inconsistentes.
- **Recomendação:** centralizar erros e aplicar exclusão transacional ou política explícita de relacionamento.

### [LOW] Nomes pouco descritivos no checkout

- **Arquivo:** `src/AppManager.js:29-46`
- **Evidência:** os dados são chamados de `u`, `e`, `p`, `cid` e `cc`.
- **Descrição:** abreviações escondem significado e sensibilidade dos valores.
- **Impacto:** aumenta o esforço de leitura e o risco de uso incorreto.
- **Recomendação:** usar nomes completos como `email`, `courseId` e `cardNumber`.

### [LOW] Estado global e exportação sem uso

- **Arquivo:** `src/utils.js:9-15`, `src/utils.js:25`, `src/AppManager.js:2`
- **Evidência:** `globalCache` cresce sem limite e `totalRevenue` é importado sem uso.
- **Descrição:** o módulo mantém estado e dependências que não sustentam o comportamento necessário.
- **Impacto:** consome memória e confunde responsabilidades.
- **Recomendação:** remover código morto e o cache, salvo necessidade comprovada.

## APIs e dependências deprecated

- A instalação sinalizou `tar`, `rimraf`, `prebuild-install`, `npmlog`, `inflight`, `glob`, `gauge` e `are-we-there-yet` como deprecated em dependências transitivas.
- `npm audit` indicou 13 vulnerabilidades: 2 baixas, 5 moderadas e 6 altas.
- Revisar atualização compatível de `sqlite3` e sua árvore. Não executar `npm audit fix --force` sem validar breaking changes.

## Escopo recomendado para a Fase 3

- Extrair configuração para ambiente e remover logs sensíveis.
- Separar app, routes, controllers, models, services e middleware de erros.
- Proteger ou retirar rotas administrativas não autenticadas.
- Usar `crypto.scrypt` com salt para senhas.
- Tornar checkout e exclusões atômicos.
- Substituir N+1 por JOIN.
- Remover cache e exportações sem uso.

## Validação planejada

- Instalação: `npm install`
- Seed: automática em banco SQLite em memória
- Boot: `npm start`
- Testes: não existem testes automatizados no baseline
- Endpoints: `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id`

## Resultado da Fase 3

- Estrutura MVC criada em `src/`.
- Configuração administrativa extraída para variável de ambiente.
- App, routes, controllers, models, services e middlewares separados.
- Checkout envolvido em transação atômica.
- Senhas protegidas com `crypto.scrypt` e salt aleatório.
- Logs de cartão e secrets removidos.
- Relatório financeiro refeito com JOIN único.
- Relatório e exclusão protegidos por `X-Admin-Token`.
- Exclusão de usuário também remove matrículas e pagamentos em transação.
- Estado global e código morto removidos.
- Os 10 findings originais foram corrigidos na reauditoria.

### Validação executada

- Sintaxe dos arquivos JavaScript: PASS.
- `npm start`: PASS.
- Relatório sem token: HTTP 401.
- Relatório com token: HTTP 200.
- Checkout aprovado: HTTP 200.
- Checkout recusado: HTTP 400.
- Exclusão administrativa: HTTP 200.
- Caminhos públicos originais preservados.

### Dependências após correção

- `npm audit fix` aplicou correções compatíveis sem `--force`.
- SQLite foi atualizado explicitamente de 5.x para 6.0.1, compatível com o requisito Node 20+.
- Checkout, relatório e exclusão foram revalidados após a atualização.
- `npm audit` final: 0 vulnerabilidades.
