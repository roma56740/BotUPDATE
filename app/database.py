import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def init_db():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            role TEXT,
            full_name TEXT,
            hearts INTEGER DEFAULT 3,
            penalty INTEGER DEFAULT 0
        )
    ''')
    conn.commit()

def add_user(user_id, username, role, full_name):
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, username, role, full_name, hearts, penalty)
        VALUES (?, ?, ?, ?, 3, 0)
    ''', (user_id, username, role, full_name))
    conn.commit()

def get_user(user_id):
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()

def get_user_by_username(username):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone()

def update_user_hearts(user_id, hearts):
    cursor.execute('UPDATE users SET hearts = ? WHERE id = ?', (hearts, user_id))
    conn.commit()

def update_user_penalty(user_id, penalty):
    cursor.execute('UPDATE users SET penalty = ? WHERE id = ?', (penalty, user_id))
    conn.commit()

def get_all_users(exclude_role=None):
    if exclude_role:
        cursor.execute('SELECT * FROM users WHERE role != ?', (exclude_role,))
    else:
        cursor.execute('SELECT * FROM users')
    return cursor.fetchall()

def delete_user_by_username(username):
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
