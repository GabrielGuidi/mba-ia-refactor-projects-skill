const database = require('../database');

function findActiveById(courseId) {
    return database.get('SELECT * FROM courses WHERE id = ? AND active = 1', [courseId]);
}

module.exports = { findActiveById };
