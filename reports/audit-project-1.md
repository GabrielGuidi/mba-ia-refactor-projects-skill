# Relatório de Auditoria Arquitetural

## Projeto

- Nome: `code-smells-project`
- Stack: Python, Flask 3.1.1, Flask-CORS 5.0.1 e SQLite
- Arquivos analisados: 4
- Linhas aproximadas: 780
- Baseline: PASS. Aplicação iniciou; `GET /health` e `GET /produtos` responderam HTTP 200.

## Resumo

| Severidade | Total |
|---|---:|
| CRITICAL | 3 |
| HIGH | 2 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **10** |

## Findings

### [CRITICAL] Execução arbitrária de SQL

- **Arquivo:** `app.py:59-76`
- **Evidência:** `/admin/query` recebe o campo `sql` e o entrega diretamente a `cursor.execute()`.
- **Descrição:** qualquer comando SQL pode ser enviado por uma requisição HTTP.
- **Impacto:** permite ler, alterar ou excluir todo o banco.
- **Recomendação:** remover o endpoint genérico e criar operações administrativas explícitas, autenticadas e autorizadas.

### [CRITICAL] SQL Injection em operações públicas

- **Arquivo:** `models.py:47-50`, `models.py:109-111`, `models.py:126-129`, `models.py:289-299`
- **Evidência:** nome, descrição, e-mail, senha, categoria e termo de busca são concatenados em SQL.
- **Descrição:** entradas externas alteram a estrutura das consultas.
- **Impacto:** permite acesso indevido, corrupção de dados e bypass de login.
- **Recomendação:** usar placeholders e parâmetros em todas as queries.

### [CRITICAL] Secrets e senhas expostos

- **Arquivo:** `app.py:7`, `controllers.py:276-290`, `database.py:31`, `database.py:75-82`, `models.py:72-103`
- **Evidência:** secret hardcoded e retornado no health check; senhas em texto puro são armazenadas e serializadas.
- **Descrição:** dados de autenticação ficam disponíveis no código, banco e respostas HTTP.
- **Impacto:** compromete sessões e contas de usuários.
- **Recomendação:** carregar secret do ambiente, aplicar hash seguro e excluir senha das serializações.

### [HIGH] Rotas administrativas destrutivas sem proteção

- **Arquivo:** `app.py:47-76`
- **Evidência:** `/admin/reset-db` e `/admin/query` não verificam autenticação ou autorização.
- **Descrição:** operações administrativas estão abertas a qualquer cliente.
- **Impacto:** permite apagar ou manipular dados remotamente.
- **Recomendação:** remover a execução genérica e proteger operações indispensáveis com autenticação e autorização.

### [HIGH] Responsabilidades de domínio e infraestrutura misturadas

- **Arquivo:** `controllers.py:5-292`, `models.py:4-314`
- **Evidência:** os mesmos módulos atendem produtos, usuários, pedidos, relatórios, notificações, HTTP e banco.
- **Descrição:** controllers conhecem banco e models concentram vários domínios e regras.
- **Impacto:** aumenta acoplamento e impede testes isolados.
- **Recomendação:** separar módulos por domínio e manter routes, controllers e models com limites claros.

### [MEDIUM] Consultas N+1 ao listar pedidos

- **Arquivo:** `models.py:171-201`, `models.py:203-233`
- **Evidência:** cada pedido consulta itens e cada item consulta novamente o produto.
- **Descrição:** a quantidade de queries cresce com pedidos e itens.
- **Impacto:** degrada latência e capacidade conforme os dados aumentam.
- **Recomendação:** carregar pedidos, itens e produtos com JOIN ou consultas agrupadas.

### [MEDIUM] Conexão global compartilhada entre requisições

- **Arquivo:** `database.py:4-12`
- **Evidência:** `db_connection` é global e usa `check_same_thread=False`.
- **Descrição:** todas as requisições reutilizam a mesma conexão sem ciclo de vida controlado.
- **Impacto:** favorece concorrência insegura, transações cruzadas e testes frágeis.
- **Recomendação:** criar conexão por contexto da aplicação e fechá-la ao final da requisição.

### [MEDIUM] Tratamento de erros inconsistente

- **Arquivo:** `controllers.py:5-292`, `app.py:77-78`
- **Evidência:** exceções genéricas são capturadas repetidamente e várias respostas incluem `str(e)`.
- **Descrição:** cada endpoint decide isoladamente como tratar falhas.
- **Impacto:** vaza detalhes internos e produz respostas inconsistentes.
- **Recomendação:** centralizar erros em middleware e expor mensagens públicas estáveis.

### [LOW] Regras de domínio como valores literais

- **Arquivo:** `controllers.py:47-54`, `models.py:256-262`
- **Evidência:** limites, categorias e faixas de desconto aparecem diretamente nas condições.
- **Descrição:** regras não possuem nomes que expressem intenção.
- **Impacto:** dificulta localizar e alterar políticas com segurança.
- **Recomendação:** usar constantes nomeadas ou funções pequenas de domínio.

### [LOW] Duplicação de montagem de pedidos

- **Arquivo:** `models.py:171-233`
- **Evidência:** `get_pedidos_usuario()` e `get_todos_pedidos()` repetem a mesma serialização e consultas de itens.
- **Descrição:** duas funções mantêm praticamente o mesmo fluxo.
- **Impacto:** correções precisam ser repetidas e podem divergir.
- **Recomendação:** extrair uma única função de carregamento e serialização.

## APIs e dependências deprecated

- Nenhuma API deprecated foi confirmada no código deste projeto.
- As versões declaradas não emitiram warnings de depreciação durante instalação e baseline.

## Escopo recomendado para a Fase 3

- Remover os endpoints administrativos inseguros ou restringi-los de forma verificável.
- Extrair configuração e secrets para ambiente.
- Separar routes/views, controllers e models por domínio.
- Parametrizar todo SQL.
- Aplicar hash seguro e retirar senhas das respostas.
- Controlar conexão por contexto e centralizar erros.
- Eliminar N+1 e duplicação na leitura de pedidos.

## Validação planejada

- Instalação: `/tmp/code-smells-venv/bin/pip install -r requirements.txt`
- Seed: criação automática no primeiro boot
- Boot: `/tmp/code-smells-venv/bin/python app.py`
- Testes: não existem testes automatizados no baseline
- Endpoints: `GET /`, `GET /health`, `GET /produtos`, `GET /usuarios`, `POST /login`, CRUD de produtos e fluxo de pedidos

## Resultado da Fase 3

- Estrutura MVC criada em `src/`.
- Configuração extraída para `src/config/settings.py`.
- Persistência separada por produtos, usuários e pedidos.
- Controllers separados por domínio.
- Rotas HTTP centralizadas em `src/views/routes.py`.
- Tratamento de erros centralizado.
- SQL parametrizado e checkout de pedido transacional.
- Senhas migradas para hash seguro e removidas das respostas.
- Endpoints administrativos inseguros removidos.
- Consultas N+1 de pedidos substituídas por JOIN.
- Os 10 findings originais foram corrigidos na reauditoria.

### Validação executada

- Compilação Python: PASS.
- Smoke tests com Flask test client: PASS.
- CRUD de produtos: PASS.
- Criação de usuário e login: PASS.
- Criação, listagem e atualização de pedido: PASS.
- Endpoint administrativo removido retorna HTTP 404: PASS.
- Boot real com debug desligado: PASS.
- `GET /health`: HTTP 200.
- `GET /produtos`: HTTP 200.
- `GET /usuarios`: HTTP 200.
- `POST /login`: HTTP 200.
