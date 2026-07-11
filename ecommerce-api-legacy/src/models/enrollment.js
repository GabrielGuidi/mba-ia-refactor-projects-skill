const database = require('../database');

async function createWithPayment(userId, course, status) {
    const enrollment = await database.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, course.id],
    );
    await database.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollment.lastID, course.price, status],
    );
    await database.run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [`Checkout curso ${course.id} por ${userId}`],
    );
    return enrollment.lastID;
}

module.exports = { createWithPayment };
