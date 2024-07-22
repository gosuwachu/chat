import logging
from .db import get_db

import redis
import json
from datetime import datetime
from flask import current_app

SYSTEM_USER_ID=1

redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

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

def get_participants(room_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT user_id FROM participant WHERE room_id = ?', (room_id,))
    return [p[0] for p in cursor.fetchall()]

def get_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM user')
    return [u[0] for u in cursor.fetchall()]

def send_message(room_id, author_id, text):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO message (room_id, author_id, text) VALUES (?, ?, ?)', (room_id, author_id, text))
    db.commit()

    message_id = cursor.lastrowid

    cursor.execute('SELECT created_at FROM message WHERE id = ?', (message_id,))
    created_at: datetime = cursor.fetchone()[0]

    enqueue_for_participants(room_id, {
        'message': {
            'room_id': room_id,
            'author_id': author_id,
            'author_name': get_user_name(author_id),
            'id': message_id,
            'text': text,
            'created_at': created_at.isoformat()
        }
    })

# TODO: enqueue only on open connections 

def enqueue_for_all_users(event):
    user = get_users()
    for user_id in user:
        __enqueue_event(user_id, json.dumps(event))

def enqueue_for_participants(room_id, event):
    participants = get_participants(room_id)
    for participant_id in participants:
        __enqueue_event(participant_id, json.dumps(event))

def __enqueue_event(user_id, event):
    current_app.logger.info(f"{event=}")
    redis_client.rpush(f'user:{user_id}', event)