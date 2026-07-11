const userModel = require('../models/user');
const { AppError } = require('../middlewares/error-handler');

async function remove(request, response, next) {
    try {
        const result = await userModel.removeWithRelations(request.params.id);
        if (!result.changes) throw new AppError('Usuário não encontrado', 404);
        return response.json({ message: 'Usuário deletado com sucesso' });
    } catch (error) {
        return next(error);
    }
}

module.exports = { remove };
