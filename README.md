# Refactor Arch: Auditoria e Refatoração MVC

Este repositório apresenta uma skill para analisar, auditar e refatorar projetos legados. A implementação foi validada em duas aplicações Python/Flask e uma aplicação Node.js/Express.

## Objetivo

A skill é capaz de:

- Analisar uma codebase e detectar linguagem, framework e arquitetura atual.
- Identificar anti-patterns e code smells com severidade, arquivo e linha.
- Gerar um relatório estruturado com os achados.
- Refatorar o projeto para o padrão MVC.
- Validar que a aplicação continua funcionando após as mudanças.

A skill é agnóstica de tecnologia e adapta o fluxo à stack detectada.

## Análise Manual

Os três projetos foram executados antes da análise. Os endpoints principais responderam com sucesso, formando o baseline para comparar a refatoração.

### Projeto 1: `code-smells-project`

Stack: Python, Flask 3.1.1, Flask-CORS e SQLite. Foram analisados 4 arquivos Python, com 780 linhas.

#### CRITICAL

- **Execução arbitrária de SQL** (`app.py:59-76`): o endpoint `/admin/query` executa o SQL recebido no corpo da requisição. Um cliente pode ler, alterar ou excluir todo o banco.
- **SQL Injection em operações públicas** (`models.py:47-50`, `models.py:109-111`, `models.py:126-129`, `models.py:289-299`): dados recebidos pela API são concatenados em consultas. Isso permite manipular comandos e acessar dados indevidos.

#### HIGH

- **Credenciais e senhas expostas** (`app.py:7`, `controllers.py:276-290`, `database.py:31`, `database.py:75-82`, `models.py:72-87`): a chave secreta está no código e no health check. Senhas são armazenadas e retornadas em texto puro, comprometendo sessões e usuários.

#### MEDIUM

- **Consultas N+1 ao listar pedidos** (`models.py:171-201`, `models.py:203-233`): cada pedido consulta seus itens e cada item consulta o produto. O custo cresce rapidamente com a quantidade de registros.
- **Tratamento de erros expõe detalhes internos** (`controllers.py:5-292`, `app.py:77-78`): exceções genéricas são repetidas e devolvidas diretamente ao cliente. Isso vaza informações internas e gera respostas inconsistentes.

#### LOW

- **Números e listas de domínio embutidos** (`controllers.py:47-54`, `models.py:256-262`): limites, categorias e faixas de desconto aparecem como valores literais. As regras ficam difíceis de localizar e alterar.
- **Arquivos e funções pouco coesos** (`controllers.py:5-292`, `models.py:4-314`, `models.py:133-169`): produtos, usuários, pedidos, relatórios e infraestrutura dividem os mesmos módulos. Isso dificulta testes e mudanças isoladas.

### Projeto 2: `ecommerce-api-legacy`

Stack: Node.js, Express 4.18.2 e SQLite3 5.1.6. Foram analisados 3 arquivos JavaScript, com 180 linhas.

#### CRITICAL

- **Secrets de produção hardcoded** (`src/utils.js:1-7`): credenciais de banco e uma chave live do gateway estão versionadas. Qualquer acesso ao repositório compromete esses serviços.
- **Cartão e chave de pagamento registrados no log** (`src/AppManager.js:28-46`): o checkout imprime o cartão completo junto da chave do gateway. Isso expõe dados financeiros sensíveis.

#### HIGH

- **Armazenamento inseguro de senhas** (`src/AppManager.js:18`, `src/AppManager.js:66-72`, `src/utils.js:17-23`): há senha seed em texto puro e a função de hash apenas repete Base64. As senhas podem ser recuperadas facilmente.

#### MEDIUM

- **Checkout sem transação atômica** (`src/AppManager.js:43-63`): matrícula, pagamento e auditoria são gravados separadamente. Uma falha intermediária deixa dados inconsistentes.
- **Consultas N+1 no relatório financeiro** (`src/AppManager.js:80-128`): cada curso consulta matrículas e cada matrícula consulta usuário e pagamento. O número de callbacks e consultas cresce com os dados.

#### LOW

- **Nomes pouco descritivos** (`src/AppManager.js:29-46`): variáveis como `u`, `e`, `p`, `cid` e `cc` escondem o significado dos dados e dificultam a leitura do checkout.
- **Estado global e exportações sem uso** (`src/utils.js:9-15`, `src/utils.js:25`, `src/AppManager.js:2`): o cache global cresce sem limite e `totalRevenue` não participa do fluxo. Isso mantém estado e dependências desnecessárias.

O `npm audit` também indicou 13 vulnerabilidades: 2 baixas, 5 moderadas e 6 altas. A instalação sinalizou dependências deprecated ligadas às versões de `package.json:10-11`.

### Projeto 3: `task-manager-api`

Stack: Python, Flask 3.0.0, Flask-SQLAlchemy 3.1.1 e SQLite. Foram analisados 16 arquivos Python, com 1.158 linhas.

#### CRITICAL

- **Autenticação falsa e rotas sem autorização** (`routes/user_routes.py:42-86`, `routes/user_routes.py:92-151`, `routes/user_routes.py:185-211`, `routes/task_routes.py:85-238`): o login retorna um token previsível que nunca é validado. Qualquer cliente pode criar administradores, alterar roles e excluir dados.
- **Hashes de senha expostos e MD5 inseguro** (`models/user.py:16-32`, `routes/user_routes.py:27-40`, `routes/user_routes.py:74-86`, `routes/user_routes.py:127-129`, `routes/user_routes.py:207-210`): a serialização inclui o hash MD5 sem salt. Isso facilita ataques offline às credenciais.

#### HIGH

- **Configuração sensível hardcoded** (`app.py:11-15`, `services/notification_service.py:4-17`): secret, credenciais SMTP e debug estão fixos no código. Isso expõe credenciais e facilita execução insegura.

#### MEDIUM

- **Consultas N+1 em listagens e relatórios** (`routes/task_routes.py:11-59`, `routes/user_routes.py:10-25`, `routes/report_routes.py:53-68`, `routes/report_routes.py:157-165`): loops consultam relacionamentos e contagens individualmente. O custo cresce com cada registro.
- **APIs deprecated de data e ORM** (`models/task.py:15-16`, `models/task.py:50-53`, `models/user.py:14`, `models/category.py:11`, `routes/task_routes.py:31-32`, `routes/task_routes.py:67`, `routes/task_routes.py:158`, `routes/user_routes.py:29`, `seed.py:66-74`): `datetime.utcnow()` e `Query.get()` geram alertas e aumentam o risco de quebra em atualizações.

#### LOW

- **Regras e serialização duplicadas** (`models/task.py:23-60`, `routes/task_routes.py:11-80`, `routes/task_routes.py:85-215`, `routes/user_routes.py:153-183`, `utils/helpers.py:57-108`): cálculo de atraso, serialização e validações aparecem em vários locais. Isso favorece divergências.
- **Imports e estado sem uso** (`app.py:7`, `routes/task_routes.py:7`, `routes/user_routes.py:6`, `routes/report_routes.py:7-8`, `utils/helpers.py:3-7`): dependências não utilizadas adicionam ruído e escondem o fluxo real.

## Construção da Skill

A ferramenta escolhida foi o **OpenAI Codex**. O desafio permite Codex e orienta adaptar a convenção usada nos exemplos de Claude Code.

A skill foi dividida em um arquivo de orquestração e cinco referências. Essa divisão mantém o fluxo principal curto e carrega detalhes somente na fase necessária.

### Estrutura

```text
.agents/skills/refactor-arch/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── project-analysis.md
    ├── anti-pattern-catalog.md
    ├── audit-report-template.md
    ├── mvc-guidelines.md
    └── refactoring-playbook.md
```

- `SKILL.md`: executa análise, auditoria, confirmação e refatoração em ordem.
- `project-analysis.md`: detecta stack, domínio, banco, arquitetura e baseline.
- `anti-pattern-catalog.md`: define 14 problemas, sinais, impacto e severidade.
- `audit-report-template.md`: padroniza findings, resumo e plano de validação.
- `mvc-guidelines.md`: delimita config, models, controllers, routes, services e middlewares.
- `refactoring-playbook.md`: descreve 12 transformações com exemplos antes e depois.

O Codex descobre skills do repositório em `.agents/skills/`. A invocação explícita usa `$refactor-arch`; `/skills` permite localizar a skill na CLI ou IDE.

### Decisões de design

- Exigir evidência por arquivo e linha para evitar findings genéricos.
- Separar detecção de transformação. Um problema pode existir em qualquer stack, mas sua correção depende da tecnologia.
- Exigir baseline antes de alterar código e repetir a mesma validação depois.
- Bloquear a Fase 3 até a resposta literal `y`.
- Preservar estruturas válidas. O Task Manager foi melhorado sem recriar seus models e blueprints.
- Usar recursos nativos ou já instalados: placeholders do SQLite, `crypto.scrypt`, Werkzeug e `itsdangerous`.

### Anti-patterns escolhidos

O catálogo cobre segurança, arquitetura, performance e qualidade:

- SQL Injection e execução arbitrária de SQL.
- Secrets e dados sensíveis expostos.
- Autenticação ou criptografia quebrada.
- God Class, God File e God Method.
- Lógica de negócio presa ao HTTP.
- Estado global e acoplamento rígido.
- Validação incompleta.
- Consultas N+1.
- Ausência de transação.
- Erros inconsistentes.
- APIs ou dependências deprecated.
- Duplicação, valores mágicos, nomes ruins e código morto.

### Independência de tecnologia

A skill usa evidências conceituais antes de exemplos de framework. Ela identifica responsabilidades, fluxo HTTP, persistência, configuração e integrações. Depois escolhe a transformação compatível com a stack encontrada.

Essa estratégia foi validada em:

- Python com SQL direto e Flask.
- Node.js com callbacks, Express e SQLite.
- Python com Flask-SQLAlchemy e organização parcial.

### Desafios e ajustes

- O projeto 1 possuía banco legado com senhas em texto puro. A inicialização passou a migrar os valores para hashes sem apagar dados.
- O middleware inicial do projeto 1 transformava 404 em 500. O handler foi ajustado para preservar exceções HTTP.
- O checkout Node.js precisou incluir criação de usuário, matrícula, pagamento e auditoria na mesma transação.
- O seed do Task Manager importava `db` do entry point. O import foi corrigido para usar a extensão diretamente.
- O audit inicial encontrou 13 vulnerabilidades Node.js. Correções compatíveis foram aplicadas sem `--force`; depois, SQLite foi atualizado explicitamente para 6.0.1 e os endpoints foram revalidados. O audit final encontrou 0 vulnerabilidades.

## Resultados

### Projeto 1: `code-smells-project`

- Auditoria: 10 findings, sendo 3 `CRITICAL`, 2 `HIGH`, 3 `MEDIUM` e 2 `LOW`.
- Antes: 4 arquivos misturavam HTTP, domínio, banco e configuração.
- Depois: estrutura MVC em `src/`, separada por configuração, models, controllers, views e middlewares.
- Segurança: SQL parametrizado, senhas com hash seguro, secrets fora do código e endpoints administrativos preservados com autenticação e operações permitidas.
- Performance: consulta N+1 de pedidos substituída por JOIN.
- Validação: compilação, smoke tests, CRUD, login, pedidos e boot real aprovados.
- Relatório: [`reports/audit-project-1.md`](reports/audit-project-1.md).

### Projeto 2: `ecommerce-api-legacy`

- Auditoria: 10 findings, sendo 3 `CRITICAL`, 2 `HIGH`, 3 `MEDIUM` e 2 `LOW`.
- Antes: uma God Class reunia banco, rotas, checkout, relatório e exclusão.
- Depois: estrutura MVC com routes, controllers, models, services e middlewares.
- Segurança: secrets fora do código, logs sensíveis removidos, senhas com `scrypt` e rotas administrativas protegidas.
- Integridade: checkout e exclusão passaram a usar transações.
- Performance: relatório N+1 substituído por JOIN.
- Validação: sintaxe, boot, checkout aprovado e recusado, relatório e exclusão aprovados.
- Dependências: Express corrigido por `npm audit fix` e SQLite atualizado explicitamente para 6.0.1; `npm audit` retorna 0 vulnerabilidades.
- Relatório: [`reports/audit-project-2.md`](reports/audit-project-2.md).

### Projeto 3: `task-manager-api`

- Auditoria: 10 findings, sendo 3 `CRITICAL`, 2 `HIGH`, 3 `MEDIUM` e 2 `LOW`.
- Antes: MVC parcial, com lógica de negócio concentrada nas routes e sem controllers.
- Depois: models e routes preservados, com controllers, config e middlewares adicionados.
- Segurança: tokens assinados, autorização por role, hash seguro e secrets fora do código.
- Performance: relacionamentos carregados com tarefas e consultas agregadas nas listagens.
- Compatibilidade: `datetime.utcnow()` e `Query.get()` substituídos.
- Validação: seed, boot, autenticação, CRUD, busca, estatísticas e relatórios aprovados.
- Relatório: [`reports/audit-project-3.md`](reports/audit-project-3.md).

### Comparação geral

| Projeto | Antes | Depois | Validação |
|---|---|---|---|
| `code-smells-project` | Monólito por tipo técnico | MVC por domínio | PASS |
| `ecommerce-api-legacy` | God Class | MVC com services | PASS |
| `task-manager-api` | MVC parcial sem controllers | MVC completo aproveitando a estrutura | PASS |

### Evidências de execução

Os trechos abaixo foram capturados após a refatoração final.

#### Projeto 1

```text
* Serving Flask app 'src.app'
* Debug mode: off
* Running on http://127.0.0.1:5000
GET /health -> HTTP 200
GET /produtos -> HTTP 200
POST /admin/query -> HTTP 200
POST /admin/reset-db -> HTTP 200
```

Os endpoints administrativos foram executados com `X-Admin-Token` e banco descartável.

#### Projeto 2

```text
> npm start
LMS rodando na porta 3000.
POST /api/checkout -> HTTP 200
GET /api/admin/financial-report -> HTTP 200
DELETE /api/users/2 -> HTTP 200
found 0 vulnerabilities
```

#### Projeto 3

```text
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
* Serving Flask app 'src_app'
* Debug mode: off
* Running on http://127.0.0.1:5000
GET /health -> HTTP 200
GET /tasks -> HTTP 200
GET /reports/summary -> HTTP 200
POST /login -> HTTP 200
```

### Checklist de validação

| Critério | Projeto 1 | Projeto 2 | Projeto 3 |
|---|:---:|:---:|:---:|
| Linguagem e framework detectados | ✅ | ✅ | ✅ |
| Domínio identificado | ✅ | ✅ | ✅ |
| Contagem de arquivos confirmada | ✅ | ✅ | ✅ |
| Pelo menos 5 findings | ✅ | ✅ | ✅ |
| Pelo menos 1 `CRITICAL` ou `HIGH` | ✅ | ✅ | ✅ |
| Arquivo e linha em cada finding | ✅ | ✅ | ✅ |
| Pausa antes da Fase 3 | ✅ | ✅ | ✅ |
| Estrutura MVC | ✅ | ✅ | ✅ |
| Configuração sem secrets hardcoded | ✅ | ✅ | ✅ |
| Models, controllers e routes separados | ✅ | ✅ | ✅ |
| Tratamento de erros centralizado | ✅ | ✅ | ✅ |
| Aplicação iniciou sem erros | ✅ | ✅ | ✅ |
| Endpoints validados | ✅ | ✅ | ✅ |

## Como Executar

### Pré-requisitos

- Python 3.12 ou compatível.
- Node.js 20.17 ou superior.
- npm.
- OpenAI Codex com suporte a skills.
- Git.

### Executar a skill

Inicie o Codex dentro de cada projeto:

```bash
cd code-smells-project
codex

cd ../ecommerce-api-legacy
codex

cd ../task-manager-api
codex
```

Em cada sessão, invoque:

```text
$refactor-arch
```

Se a skill não aparecer, use `/skills` para confirmar a descoberta.

### Validar o projeto 1

```bash
cd code-smells-project
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="uma-chave-local-segura"
export ADMIN_TOKEN="um-token-administrativo-local"
python app.py
```

A aplicação inicia em `http://localhost:5000`. Enviar `X-Admin-Token` nos endpoints `/admin/reset-db` e `/admin/query`.

### Validar o projeto 2

```bash
cd ecommerce-api-legacy
npm install
export ADMIN_TOKEN="um-token-administrativo-local"
npm start
```

A aplicação inicia em `http://localhost:3000`. Enviar `X-Admin-Token` no relatório financeiro e na exclusão de usuários.

### Validar o projeto 3

```bash
cd task-manager-api
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="uma-chave-local-segura"
python seed.py
python app.py
```

A aplicação inicia em `http://localhost:5000`. Obter o token em `POST /login` e enviar `Authorization: Bearer <token>` nas rotas protegidas.
