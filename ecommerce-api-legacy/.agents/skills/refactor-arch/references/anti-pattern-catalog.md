# Catálogo de anti-patterns

Classificar pela evidência e pelo impacto real. Ajustar a severidade quando o contexto reduzir ou ampliar o risco.

## CRITICAL

### Execução arbitrária ou SQL Injection

- Sinais: SQL recebido por HTTP; concatenação, interpolação ou template com entrada externa.
- Python: `cursor.execute("..." + request.args["q"])`.
- Node.js: ``db.all(`... ${req.body.value}`)``.
- Impacto: leitura, alteração ou destruição de dados.
- Recomendação: remover execução genérica e usar queries parametrizadas.

### Secrets ou dados sensíveis expostos

- Sinais: secret, senha, token, cartão ou chave live no código, resposta ou log.
- Python: `app.config["SECRET_KEY"] = "..."`.
- Node.js: `console.log(card, paymentKey)`.
- Impacto: comprometimento de contas, sessões ou serviços.
- Recomendação: revogar secrets, usar ambiente e aplicar redação em logs.

### Autenticação ou criptografia quebrada

- Sinais: token previsível, ausência de validação, senha em texto puro, MD5, SHA-1 ou Base64 como hash.
- Python: `hashlib.md5(password).hexdigest()`.
- Node.js: `Buffer.from(password).toString("base64")`.
- Impacto: tomada de conta e elevação de privilégio.
- Recomendação: usar autenticação verificável, autorização e função própria para senhas.

## HIGH

### God Class, God File ou God Method

- Sinais: um módulo reúne rotas, SQL, domínio, configuração e integrações; função longa com muitos motivos para mudar.
- Python: um `controllers.py` atende todos os domínios e acessa banco.
- Node.js: classe configura banco e declara todas as rotas.
- Impacto: alto acoplamento e testes difíceis.
- Recomendação: separar por responsabilidade e domínio.

### Lógica de negócio em route/controller HTTP

- Sinais: cálculos, políticas, transações ou loops de domínio junto de request e response.
- Python: route calcula relatório e grava models.
- Node.js: callback Express processa pagamento e matrícula.
- Impacto: domínio preso ao framework e difícil de testar.
- Recomendação: extrair caso de uso para controller ou service.

### Estado global mutável ou acoplamento rígido

- Sinais: conexão, cache ou coleção global; dependência criada dentro da classe e impossível de substituir.
- Python: `global db_connection` compartilhada entre requisições.
- Node.js: `globalCache = {}` sem limite ou ciclo de vida.
- Impacto: concorrência insegura, vazamento de memória e testes frágeis.
- Recomendação: usar ciclo de vida do framework e injetar dependências essenciais.

## MEDIUM

### Validação ausente ou incompleta

- Sinais: acesso a `request.body`, JSON ou query sem tipo, faixa ou formato; conversão que pode lançar erro.
- Python: `int(request.args["priority"])` sem tratamento.
- Node.js: aceitar role, quantidade ou identificador sem validar.
- Impacto: erros 500, dados inválidos ou abuso do fluxo.
- Recomendação: validar na fronteira HTTP antes do caso de uso.

### Consultas N+1

- Sinais: query dentro de loop de entidades ou relacionamentos carregados individualmente.
- Python: `for task: User.query.get(task.user_id)`.
- Node.js: `forEach(enrollment => db.get(...))`.
- Impacto: latência e carga crescentes.
- Recomendação: JOIN, eager loading ou agregação.

### Ausência de transação

- Sinais: caso de uso grava múltiplas tabelas e confirma parcialmente.
- Python: vários commits em uma operação lógica.
- Node.js: matrícula e pagamento sem `BEGIN/ROLLBACK`.
- Impacto: dados inconsistentes após falha intermediária.
- Recomendação: delimitar uma transação atômica.

### Tratamento de erros inconsistente

- Sinais: `except` ou `catch` genérico repetido, erro interno devolvido, callback ignora `err`.
- Python: `jsonify({"error": str(e)})`.
- Node.js: continuar após erro de banco.
- Impacto: vazamento de detalhes e respostas instáveis.
- Recomendação: middleware/handler central e erros de domínio explícitos.

### API ou dependência deprecated

- Sinais: warnings de runtime, documentação oficial marcando depreciação, pacote sem suporte ou audit do gerenciador.
- Python: `datetime.utcnow()` ou `Query.get()` quando a versão instalada recomenda substituto.
- Node.js: pacote ou API marcada deprecated durante instalação.
- Impacto: quebra futura e vulnerabilidades sem correção.
- Recomendação: usar equivalente moderno confirmado pela versão do projeto.

## LOW

### Duplicação

- Sinais: mesma validação, serialização ou regra em dois ou mais locais.
- Impacto: divergência e manutenção repetida.
- Recomendação: reutilizar função pequena já existente ou extrair uma.

### Magic numbers e strings

- Sinais: faixas, status, percentuais e limites sem nome em lógica de domínio.
- Impacto: intenção escondida e mudança arriscada.
- Recomendação: constante nomeada ou função de política.

### Nomes pouco descritivos e código morto

- Sinais: `u`, `p`, `x`, imports, exports ou variáveis sem uso.
- Impacto: leitura mais lenta e dependências confusas.
- Recomendação: renomear valores ativos e remover código sem uso.

## Regra de evidência

Todo finding deve conter arquivo. Usar linha exata para expressão e intervalo para função ou classe. Não criar finding apenas porque uma pasta MVC não existe.
