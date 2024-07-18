import sqlite3
from dataclasses import dataclass

from flask import (
    Blueprint, current_app, request, jsonify
)

from .db import get_db

bp = Blueprint('api', __name__, url_prefix='/')


@dataclass
class User:
    id: int
    name: str


@bp.route("/user/create", methods=['POST'])
def create_user():
    name = request.get_json()["name"]

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO user (name) VALUES (?)', (name,))
        db.commit()

        return {"id": cursor.lastrowid}
    except sqlite3.IntegrityError as ex:
        if ex.sqlite_errorname == 'SQLITE_CONSTRAINT_UNIQUE':
            return jsonify({'error': 'user already exists'}), 400
        raise


@bp.route("/user", methods=['GET'])
def users():
    db = get_db()
    result = db.execute('SELECT * FROM user').fetchall()
    return jsonify([ dict(**row) for row in result])


@bp.route("/room/create", methods=['POST'])
def create_room():
    name = request.get_json()["name"]
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO room (name) VALUES (?)', (name,))
        db.commit()

        return {"id": cursor.lastrowid}
    except sqlite3.IntegrityError as ex:
        if ex.sqlite_errorname == 'SQLITE_CONSTRAINT_UNIQUE':
            return jsonify({'error': 'room already exists'}), 400
        raise


@bp.route("/room/<int:room_id>/join/<int:user_id>", methods=['POST'])
def join_room(room_id, user_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO participant (room_id, user_id) VALUES (?, ?)', (room_id, user_id))
        db.commit()

        return {}
    except sqlite3.IntegrityError as ex:
        current_app.logger.exception("An unexpected error occurred")
        return jsonify({'error': 'an error occurred while processing your request.'}), 500


@bp.route("/room/<int:room_id>/leave/<int:user_id>", methods=['POST'])
def leave_room(room_id, user_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM participant WHERE room_id = ? AND user_id = ?', (room_id, user_id))
        db.commit()

        return {}
    except sqlite3.IntegrityError as ex:
        current_app.logger.exception("An unexpected error occurred")
        return jsonify({'error': 'an error occurred while processing your request.'}), 500


@bp.route("/room", methods=['GET'])
def rooms():
    db = get_db()
    result = db.execute('SELECT * FROM room').fetchall()
    return jsonify([ dict(**row) for row in result])


@bp.route("/room/<int:room_id>/participants", methods=['GET'])
def room_participants(room_id):
    db = get_db()
    result = db.execute(
        'SELECT user.id, user.name FROM user ' +
        'JOIN participant ON user.id = participant.user_id ' + 
        'JOIN room ON participant.room_id = room.id ' + 
        'WHERE room.id = ?;', (room_id,)).fetchall()
    return jsonify([ dict(**row) for row in result])


@bp.route("/room/<int:room_id>/message", methods=['GET'])
def get_messages(room_id):
    db = get_db()
    result = db.execute(
        'SELECT message.id, message.created_at, message.text, user.name AS author_name ' +
        'FROM message ' +
        'JOIN user ON message.author_id = user.id ' +
        'WHERE message.room_id = ?;', (room_id,)).fetchall()
    return jsonify([ dict(**row) for row in result])


@bp.route("/room/<int:room_id>/user/<int:author_id>/message", methods=['POST'])
def send_message(room_id, author_id):
    text = request.get_json()["text"]

    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO message (room_id, author_id, text) VALUES (?, ?, ?)', (room_id, author_id, text))
        db.commit()

        return {}
    except sqlite3.IntegrityError as ex:
        current_app.logger.exception("An unexpected error occurred")
        return jsonify({'error': 'an error occurred while processing your request.'}), 500