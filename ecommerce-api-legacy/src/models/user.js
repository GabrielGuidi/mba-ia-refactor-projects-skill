const database = require('../database');

function findByEmail(email) {
    return database.get('SELECT id FROM users WHERE email = ?', [email]);
}

async function create(name, email, passwordHash) {
    const result = await database.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, passwordHash],
    );
    return result.lastID;
}

async function removeWithRelations(userId) {
    return database.transaction(async () => {
        const enrollments = await database.all('SELECT id FROM enrollments WHERE user_id = ?', [userId]);
        for (const enrollment of enrollments) {
            await database.run('DELETE FROM payments WHERE enrollment_id = ?', [enrollment.id]);
        }
        await database.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
        return database.run('DELETE FROM users WHERE id = ?', [userId]);
    });
}

module.exports = { findByEmail, create, removeWithRelations };
