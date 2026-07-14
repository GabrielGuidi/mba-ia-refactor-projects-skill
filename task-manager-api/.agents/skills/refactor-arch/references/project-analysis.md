# Análise de projeto

## Ordem de inspeção

1. Listar arquivos até profundidade suficiente para entender o projeto.
2. Ler manifestos e documentação de execução.
3. Localizar entry points, rotas, models, acesso a dados e configuração.
4. Contar somente arquivos fonte próprios e suas linhas.
5. Inferir o domínio por rotas, entidades e tabelas. Não usar apenas o nome da pasta.

## Evidências de stack

| Evidência | Conclusão provável |
|---|---|
| `requirements.txt`, `pyproject.toml`, `.py` | Python |
| importação de `flask`, `Flask(...)` | Flask |
| `package.json`, `.js`, `.mjs`, `.ts` | Node.js |
| dependência `express`, chamada `express()` | Express |
| `sqlite3`, URI `sqlite`, arquivo `.db` | SQLite |
| `SQLAlchemy`, `db.Model` | SQLAlchemy |

Confirmar versões nos manifestos ou no gerenciador de pacotes. Não estimar versão.

## Arquitetura atual

Classificar pela responsabilidade observada:

- **Monolítica:** HTTP, domínio e banco concentrados nos mesmos arquivos.
- **Separada por tipo:** rotas, models ou serviços existem, mas responsabilidades ainda se misturam.
- **MVC parcial:** camadas existem, porém faltam controllers, configuração ou limites claros.
- **MVC:** rotas adaptam HTTP, controllers orquestram e models abstraem dados.

Registrar desvios concretos. O nome de uma pasta não prova sua responsabilidade.

## Mapeamento

- Endpoints: método, caminho, função e arquivo.
- Domínio: entidades e casos de uso.
- Dados: banco, tabelas, models, seeds e migrações.
- Integrações: e-mail, pagamentos, APIs externas e filas.
- Configuração: secrets, portas, debug e variáveis de ambiente.
- Validação: testes, arquivos HTTP, scripts e health checks.

## Baseline

Executar o caminho documentado pelo projeto. Registrar:

- instalação de dependências;
- seed ou criação do banco;
- comando de boot;
- endpoints representativos por método;
- status HTTP e propriedades essenciais da resposta.

Evitar endpoints destrutivos. Se forem indispensáveis, usar dados descartáveis.

## Formato da saída

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem e versão, se confirmada>
Framework:     <framework e versão>
Dependencies:  <dependências principais>
Domain:        <domínio inferido>
Architecture:  <classificação e justificativa curta>
Source files:  <quantidade> files analyzed
Source lines:  <quantidade aproximada>
Database:      <tecnologia e tabelas/models>
Entry point:   <arquivo e comando>
Baseline:      <PASS, FAIL ou NOT RUN, com motivo>
================================
```
