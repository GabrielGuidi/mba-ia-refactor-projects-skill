# Guidelines MVC

MVC aqui define limites de responsabilidade, não quantidade fixa de arquivos.

## Responsabilidades

### Config

- Ler ambiente e fornecer valores tipados.
- Manter caminhos, portas e flags.
- Nunca conter secrets reais como fallback.

### Models

- Representar entidades e acesso a dados.
- Usar queries parametrizadas.
- Preservar invariantes próximas dos dados.
- Não conhecer request, response ou códigos HTTP.

### Controllers

- Orquestrar casos de uso.
- Validar regras de aplicação que dependem de mais de uma entidade.
- Chamar models e services.
- Retornar resultado independente do framework quando possível.
- Não conter SQL.

### Views ou Routes

- Declarar método e caminho.
- Ler entrada HTTP e executar validação de fronteira.
- Chamar controller.
- Converter resultado em resposta HTTP.
- Não conter regra de negócio pesada.

### Services

- Encapsular integrações e políticas reutilizadas por casos de uso.
- Criar somente quando houver responsabilidade real, como pagamento ou e-mail.

### Middlewares

- Centralizar erros, autenticação, autorização e preocupações HTTP comuns.
- Não implementar caso de uso.

### Entry point

- Criar a aplicação.
- Inicializar dependências.
- Registrar rotas e middlewares.
- Iniciar o servidor somente quando executado diretamente.

## Estrutura Python/Flask

```text
src/
├── app.py
├── config/
├── models/
├── controllers/
├── views/
├── services/       # somente se necessário
└── middlewares/
```

Usar blueprints em `views/`. Manter uma factory quando ela melhorar testes e configuração.

## Estrutura Node.js/Express

```text
src/
├── app.js
├── config/
├── models/
├── controllers/
├── routes/
├── services/       # somente se necessário
└── middlewares/
```

Separar criação do app de `listen` quando isso permitir testes sem abrir porta.

## Regras de migração

- Preservar caminhos, métodos, status e propriedades públicas.
- Aproveitar models, routes e services válidos existentes.
- Separar por domínio quando um arquivo atende domínios independentes.
- Preferir poucos módulos coesos a uma classe por função.
- Manter transação no limite do caso de uso.
- Centralizar erros sem esconder falhas de programação.
- Incluir configuração de ambiente sem adicionar biblioteca quando `os.environ` ou `process.env` bastar.

## Pronto quando

- entry point apenas compõe a aplicação;
- routes adaptam HTTP;
- controllers orquestram;
- models isolam persistência;
- secrets não estão no código ou respostas;
- erros seguem formato consistente;
- baseline e testes passam.
