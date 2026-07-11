const express = require('express');
const routes = require('./routes');
const { errorHandler } = require('./middlewares/error-handler');

function createApp() {
    const app = express();
    app.use(express.json());
    app.use('/api', routes);
    app.use(errorHandler);
    return app;
}

module.exports = { createApp };
