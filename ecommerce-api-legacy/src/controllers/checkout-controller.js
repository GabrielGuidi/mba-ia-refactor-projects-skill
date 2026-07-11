const courseModel = require('../models/course');
const enrollmentModel = require('../models/enrollment');
const userModel = require('../models/user');
const { AppError } = require('../middlewares/error-handler');
const { hashPassword } = require('../services/password-service');
const { processPayment } = require('../services/payment-service');
const database = require('../database');

async function checkout(request, response, next) {
    try {
        const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = request.body;
        if (!userName || !email || !password || !courseId || !cardNumber) {
            throw new AppError('Dados de checkout inválidos');
        }

        const course = await courseModel.findActiveById(courseId);
        if (!course) throw new AppError('Curso não encontrado', 404);

        const paymentStatus = processPayment(cardNumber);
        if (paymentStatus === 'DENIED') throw new AppError('Pagamento recusado');

        const passwordHash = await hashPassword(password);
        const enrollmentId = await database.transaction(async () => {
            let user = await userModel.findByEmail(email);
            if (!user) {
                const userId = await userModel.create(userName, email, passwordHash);
                user = { id: userId };
            }
            return enrollmentModel.createWithPayment(user.id, course, paymentStatus);
        });
        return response.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    } catch (error) {
        return next(error);
    }
}

module.exports = { checkout };
