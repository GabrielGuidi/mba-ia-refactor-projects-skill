const express = require('express');
const checkoutController = require('../controllers/checkout-controller');
const reportController = require('../controllers/report-controller');
const userController = require('../controllers/user-controller');
const { requireAdmin } = require('../middlewares/admin-auth');

const router = express.Router();

router.post('/checkout', checkoutController.checkout);
router.get('/admin/financial-report', requireAdmin, reportController.financialReport);
router.delete('/users/:id', requireAdmin, userController.remove);

module.exports = router;
