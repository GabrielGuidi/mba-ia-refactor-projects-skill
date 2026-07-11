# Relatório de Auditoria Arquitetural

## Projeto

- Nome: `task-manager-api`
- Stack: Python, Flask 3.0.0, Flask-SQLAlchemy 3.1.1 e SQLite
- Arquivos analisados: 16
- Linhas aproximadas: 1.158
- Baseline: PASS. Seed concluído; health, tarefas e relatório responderam HTTP 200.

## Resumo

| Severidade | Total |
|---|---:|
| CRITICAL | 3 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **10** |

## Findings

### [CRITICAL] Autenticação falsa e rotas sem autorização

- **Arquivo:** `routes/user_routes.py:42-151`, `routes/user_routes.py:185-211`, `routes/task_routes.py:85-238`
- **Evidência:** o login retorna `fake-jwt-token-<id>` e nenhuma rota valida token ou role.
- **Descrição:** qualquer cliente pode criar administradores, alterar roles e modificar ou excluir dados.
- **Impacto:** permite elevação de privilégio e controle completo da API.
- **Recomendação:** implementar token verificável e autorização por role nas operações protegidas.

### [CRITICAL] MD5 e hashes de senha expostos

- **Arquivo:** `models/user.py:16-32`, `routes/user_routes.py:27-40`, `routes/user_routes.py:74-86`, `routes/user_routes.py:127-129`, `routes/user_routes.py:207-210`
- **Evidência:** `to_dict()` inclui `password`; `set_password()` usa MD5 sem salt.
- **Descrição:** hashes rápidos são retornados por endpoints e pelo login.
- **Impacto:** facilita quebra offline e comprometimento de credenciais.
- **Recomendação:** usar hash próprio para senhas e excluir o campo de toda serialização.

### [CRITICAL] Secrets e credenciais SMTP hardcoded

- **Arquivo:** `app.py:11-15`, `services/notification_service.py:4-17`
- **Evidência:** secret da aplicação, usuário e senha SMTP estão no código.
- **Descrição:** credenciais e configuração sensível são versionadas.
- **Impacto:** compromete sessões e a conta de e-mail.
- **Recomendação:** revogar credenciais e carregar novos valores por ambiente.

### [HIGH] Regras de negócio concentradas nas routes

- **Arquivo:** `routes/task_routes.py:11-299`, `routes/user_routes.py:10-211`, `routes/report_routes.py:12-223`
- **Evidência:** routes validam, consultam, calculam relatórios, alteram models e formatam respostas.
- **Descrição:** adaptação HTTP e casos de uso não possuem limite arquitetural.
- **Impacto:** dificulta testes, reutilização e manutenção.
- **Recomendação:** manter routes finas e extrair orquestração para controllers.

### [HIGH] Tratamento de erros espalhado e genérico

- **Arquivo:** `routes/task_routes.py:62-63`, `routes/task_routes.py:146-154`, `routes/task_routes.py:217-238`, `routes/user_routes.py:80-90`, `routes/user_routes.py:127-151`, `routes/report_routes.py:182-223`
- **Evidência:** vários `except:` e blocos de rollback repetem respostas distintas.
- **Descrição:** cada endpoint decide isoladamente como tratar falhas.
- **Impacto:** erros de programação são ocultados e respostas divergem.
- **Recomendação:** centralizar exceções de aplicação e falhas inesperadas.

### [MEDIUM] Consultas N+1 em listagens e relatórios

- **Arquivo:** `routes/task_routes.py:11-59`, `routes/user_routes.py:10-25`, `routes/report_routes.py:53-68`, `routes/report_routes.py:157-165`
- **Evidência:** loops consultam usuários, categorias, tarefas e contagens individualmente.
- **Descrição:** a quantidade de queries cresce com cada registro.
- **Impacto:** aumenta latência e carga no banco.
- **Recomendação:** usar eager loading e agregações.

### [MEDIUM] APIs deprecated de data e ORM

- **Arquivo:** `models/task.py:15-16`, `models/task.py:50-53`, `models/user.py:14`, `models/category.py:11`, `routes/task_routes.py:31-32`, `routes/task_routes.py:67`, `routes/task_routes.py:158`, `routes/user_routes.py:29`, `seed.py:66-74`
- **Evidência:** o runtime sinalizou `datetime.utcnow()`; o código usa `Query.get()` legado.
- **Descrição:** APIs antigas permanecem em models, routes e seed.
- **Impacto:** gera warnings e risco de quebra em atualizações.
- **Recomendação:** usar UTC com timezone e `db.session.get()`.

### [MEDIUM] Validação de entrada inconsistente

- **Arquivo:** `routes/task_routes.py:85-145`, `routes/task_routes.py:240-271`, `routes/user_routes.py:42-78`, `routes/report_routes.py:167-203`
- **Evidência:** regras são duplicadas; conversões de query podem lançar erro; categorias aceitam cor e nome sem validação completa.
- **Descrição:** cada rota valida uma parte diferente dos dados.
- **Impacto:** permite dados inválidos e respostas 500 para entradas malformadas.
- **Recomendação:** criar validações de fronteira reutilizáveis e respostas 400 consistentes.

### [LOW] Serialização e cálculo de atraso duplicados

- **Arquivo:** `models/task.py:23-60`, `routes/task_routes.py:11-80`, `routes/user_routes.py:153-183`, `utils/helpers.py:57-108`
- **Evidência:** serialização, status de atraso e validações aparecem em vários locais.
- **Descrição:** regras equivalentes possuem implementações diferentes.
- **Impacto:** correções podem divergir entre endpoints.
- **Recomendação:** reutilizar métodos e helpers únicos.

### [LOW] Imports e estado sem uso

- **Arquivo:** `app.py:7`, `routes/task_routes.py:7`, `routes/user_routes.py:6`, `routes/report_routes.py:7-8`, `utils/helpers.py:3-7`, `services/notification_service.py:5-6`
- **Evidência:** vários imports não são usados e notificações ficam apenas em uma lista local.
- **Descrição:** dependências e estado não participam claramente do fluxo da aplicação.
- **Impacto:** adiciona ruído e esconde responsabilidades reais.
- **Recomendação:** remover código morto e manter apenas estado com ciclo de vida definido.

## APIs e dependências deprecated

- `datetime.utcnow()` emite `DeprecationWarning` no Python atual. Usar `datetime.now(UTC)` e armazenar UTC de forma consistente.
- `Model.query.get(id)` é legado no SQLAlchemy 2.x. Usar `db.session.get(Model, id)`.

## Escopo recomendado para a Fase 3

- Preservar models e blueprints úteis existentes.
- Extrair configuração e secrets.
- Implementar autenticação verificável e autorização.
- Extrair controllers para tarefas, usuários e relatórios.
- Centralizar erros e validações.
- Remover N+1 com eager loading e agregações.
- Atualizar APIs deprecated.
- Remover duplicação, imports e estado sem uso.

## Validação planejada

- Instalação: `/tmp/task-manager-venv/bin/pip install -r requirements.txt`
- Seed: `/tmp/task-manager-venv/bin/python seed.py`
- Boot: `/tmp/task-manager-venv/bin/python app.py`
- Testes: não existem testes automatizados no baseline
- Endpoints: `GET /health`, `GET /tasks`, `GET /reports/summary`, CRUD de tarefas, usuários e categorias, `POST /login`

## Resultado da Fase 3

- Estrutura existente de models, routes, services e utils preservada.
- Controllers, config e middlewares adicionados.
- Entry point reduzido à composição da aplicação.
- Tokens assinados e autorização por role implementados.
- Senhas protegidas com hash seguro e removidas das respostas.
- Configuração e SMTP extraídos para ambiente.
- Routes reduzidas à adaptação HTTP.
- Tratamento de erros centralizado.
- Relacionamentos carregados junto das tarefas e agregações usadas em listagens.
- `datetime.utcnow()` e `Query.get()` substituídos.
- Helpers, imports e duplicações principais removidos.
- Os 10 findings originais foram corrigidos na reauditoria.

### Validação executada

- Compilação Python: PASS.
- Seed: PASS, com 3 usuários, 4 categorias e 10 tarefas.
- Autenticação e autorização: PASS.
- CRUD de tarefas: PASS.
- CRUD de usuários: PASS.
- CRUD de categorias: PASS.
- Busca, estatísticas e relatórios: PASS.
- Rota protegida sem token: HTTP 401.
- Boot real com debug desligado: PASS.
- `GET /health`: HTTP 200.
- `GET /tasks`: HTTP 200.
- `GET /reports/summary`: HTTP 200.
- `POST /login`: HTTP 200.
