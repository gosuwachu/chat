from .db import get_db

SYSTEM_USER_ID=1

def get_user_name(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name FROM user WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Return the user's name
    else:
        return None  # User not found

def send_system_message(room_id, text):
    send_message(room_id, SYSTEM_USER_ID, text)

def send_message(room_id, author_id, text):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO message (room_id, author_id, text) VALUES (?, ?, ?)', (room_id, author_id, text))
    db.commit()
