const database = require('../database');

function financialRows() {
    return database.all(
        `SELECT c.id, c.title AS course, u.name AS student,
                p.amount, p.status
         FROM courses c
         LEFT JOIN enrollments e ON e.course_id = c.id
         LEFT JOIN users u ON u.id = e.user_id
         LEFT JOIN payments p ON p.enrollment_id = e.id
         ORDER BY c.id, e.id`,
    );
}

module.exports = { financialRows };
