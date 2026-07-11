const { config } = require('../config/settings');
const { AppError } = require('./error-handler');

function requireAdmin(request, _response, next) {
    if (!config.adminToken || request.get('X-Admin-Token') !== config.adminToken) {
        return next(new AppError('Não autorizado', 401));
    }
    return next();
}

module.exports = { requireAdmin };
