const { createApp } = require('./application');
const { config } = require('./config/settings');
const database = require('./database');

async function start() {
    await database.initialize();
    const app = createApp();
    return app.listen(config.port, () => {
        console.log(`LMS rodando na porta ${config.port}.`);
    });
}

if (require.main === module) {
    start().catch((error) => {
        console.error('Falha ao iniciar a aplicação.', error);
        process.exitCode = 1;
    });
}

module.exports = { start };
