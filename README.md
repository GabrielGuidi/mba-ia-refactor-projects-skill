# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

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

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
$refactor-arch
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** O enunciado original usa Claude Code como exemplo. Esta entrega escolheu OpenAI Codex e adaptou a skill para `.agents/skills/`, com invocação explícita por `$refactor-arch`.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir. Esta entrega usa a convenção do Codex: `.agents/skills/refactor-arch/`.

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Codex:

```text
$refactor-arch
```

> **Nota:** No Codex, inicie a ferramenta dentro do projeto e envie `$refactor-arch` no prompt.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.agents/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
codex
```

```text
$refactor-arch
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.agents/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
codex
```

```text
$refactor-arch
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.agents/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo está adaptada para OpenAI Codex (`.agents/skills/`).

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .agents/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .agents/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .agents/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.agents/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
codex

# Projeto 2
cd ../ecommerce-api-legacy
codex

# Projeto 3
cd ../task-manager-api
codex
```

Em cada sessão do Codex:

```text
$refactor-arch
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [OpenAI Codex: Build skills](https://learn.chatgpt.com/docs/build-skills.md) — Convenção, descoberta e invocação de skills no Codex
- [Agent Skills specification](https://agentskills.io/specification) — Especificação aberta usada pelo formato `SKILL.md`

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.
