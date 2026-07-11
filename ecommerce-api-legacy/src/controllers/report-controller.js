const reportModel = require('../models/report');

async function financialReport(_request, response, next) {
    try {
        const rows = await reportModel.financialRows();
        const byCourse = new Map();
        for (const row of rows) {
            const course = byCourse.get(row.id) || { course: row.course, revenue: 0, students: [] };
            if (row.student) {
                if (row.status === 'PAID') course.revenue += row.amount;
                course.students.push({ student: row.student, paid: row.amount || 0 });
            }
            byCourse.set(row.id, course);
        }
        return response.json([...byCourse.values()]);
    } catch (error) {
        return next(error);
    }
}

module.exports = { financialReport };
