# Playbook de refatoração

Aplicar somente padrões ligados a findings confirmados. Exemplos são ilustrativos; adaptar à stack existente.

## 1. Extrair rotas do entry point

Quando: o entry point declara muitos endpoints.

Antes, Flask:

```python
app = Flask(__name__)
app.get("/products")(list_products)
```

Depois:

```python
products = Blueprint("products", __name__)
products.get("/products")(list_products)
app.register_blueprint(products)
```

Antes, Express: `app.get('/products', handler)` no `app.js`.

Depois: `router.get('/products', handler)` em `routes/products.js`, registrado pelo app.

Destino: `views/` no Flask ou `routes/` no Express. Validar boot e rota.

## 2. Extrair lógica HTTP para controller

Quando: a route calcula regras ou coordena várias operações.

Antes:

```python
@bp.post("/orders")
def create():
    total = sum(item["price"] for item in request.json["items"])
    return save_order(total)
```

Depois:

```python
@bp.post("/orders")
def create():
    return jsonify(order_controller.create(request.get_json())), 201
```

No Express, substituir callback longo por `router.post('/orders', controller.create)`. Destino: `controllers/`. Validar status e corpo.

## 3. Extrair acesso a dados para model

Quando: route ou controller executa SQL.

Antes: `cursor.execute("SELECT * FROM products")` na route.

Depois: `products = product_model.list_all()` no controller.

No Express, mover `db.all(...)` para `models/product.js`. Validar resultado e erros.

## 4. Extrair configuração hardcoded

Quando: porta, debug, caminho ou secret está no código.

Antes, Python: `SECRET_KEY = "secret"`.

Depois:

```python
SECRET_KEY = os.environ["SECRET_KEY"]
```

Antes, Node.js: `paymentKey: "pk_live_..."`.

Depois: `paymentKey: process.env.PAYMENT_GATEWAY_KEY`.

Destino: `config/`. Falhar cedo quando secret obrigatório estiver ausente. Validar boot com ambiente de teste.

## 5. Parametrizar SQL

Quando: entrada é concatenada ou interpolada.

Antes:

```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
```

Depois:

```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
```

Express/SQLite: `db.get('... WHERE email = ?', [email], callback)`. Validar com aspas e payload de injeção.

## 6. Centralizar erros

Quando: handlers repetem `try/except` ou `try/catch` e expõem detalhes.

Antes: `return jsonify({'error': str(error)}), 500` em cada route.

Depois, Flask: registrar `@app.errorhandler(AppError)` e retornar mensagem pública.

Depois, Express: encaminhar `next(error)` e registrar middleware `(error, req, res, next)`.

Destino: `middlewares/`. Validar 400, 404 e 500.

## 7. Remover duplicação

Quando: a mesma validação ou serialização aparece em vários endpoints.

Antes: repetir cálculo de atraso em três loops.

Depois: `task.is_overdue()` ou `serialize_task(task)` usado por todos.

Destino: model para regra da entidade; controller/helper para representação. Validar respostas equivalentes.

## 8. Separar God Class ou God File por domínio

Quando: um módulo atende usuários, pedidos, pagamentos e relatórios.

Antes: `AppManager.setupRoutes()` contém todos os fluxos.

Depois:

```text
routes/checkout.js
controllers/checkout-controller.js
models/enrollment.js
services/payment-service.js
```

No Flask, usar módulos equivalentes por produto, usuário e pedido. Não criar camada vazia. Validar todos os endpoints originais.

## 9. Adicionar validação de entrada

Quando: tipo, formato, faixa ou campos obrigatórios não são verificados.

Antes: `priority = int(request.args['priority'])`.

Depois: converter em bloco controlado e retornar 400 quando inválido.

No Express, validar `req.body` antes do controller. Preferir funções pequenas; usar biblioteca apenas se já instalada. Validar casos válido, ausente e inválido.

## 10. Substituir API deprecated

Quando: warning ou documentação da versão instalada confirma depreciação.

Antes, Python:

```python
datetime.utcnow()
User.query.get(user_id)
```

Depois:

```python
datetime.now(UTC)
db.session.get(User, user_id)
```

No Node.js, atualizar a chamada ou dependência para o substituto suportado, após conferir changelog e compatibilidade. Validar testes e boot.

## 11. Tornar operação atômica

Quando: um caso de uso grava várias tabelas.

Antes: criar matrícula e pagamento sem rollback conjunto.

Depois: iniciar transação, executar todas as gravações, confirmar no fim e reverter em qualquer erro.

No SQLAlchemy, usar uma unidade de trabalho da sessão. No SQLite Node, usar `BEGIN`, `COMMIT` e `ROLLBACK`. Validar falha intermediária sem registros parciais.

## 12. Corrigir armazenamento de senha

Quando: senha está em texto puro, MD5, SHA-1 ou Base64.

Antes: `hashlib.md5(password.encode()).hexdigest()`.

Depois: usar `werkzeug.security.generate_password_hash` e `check_password_hash` no Flask.

No Node.js, usar `crypto.scrypt` da biblioteca padrão com salt aleatório. Nunca serializar o hash. Validar criação, login correto e login incorreto.
