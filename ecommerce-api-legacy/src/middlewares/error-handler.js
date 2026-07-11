class AppError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.status = status;
    }
}

function errorHandler(error, _request, response, _next) {
    if (error instanceof AppError) {
        return response.status(error.status).json({ error: error.message });
    }
    console.error('Erro interno.', error);
    return response.status(500).json({ error: 'Erro interno' });
}

module.exports = { AppError, errorHandler };
