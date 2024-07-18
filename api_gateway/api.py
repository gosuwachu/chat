import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route("/room/join", methods=['POST'])
def join_room():
    return "<p>Hello, World!</p>"

@bp.route("/room/leave", methods=['POST'])
def leave_room():
    return "<p>Hello, World!</p>"

@bp.route("/rooms", methods=['GET'])
def rooms():
    return "<p>Hello, World!</p>"

@bp.route("/room/<id>/participants", methods=['GET'])
def room_participants():
    return "<p>Hello, World!</p>"

@bp.route("/room/<id>/messages", methods=['GET'])
def get_messages():
    return "<p>Hello, World!</p>"

@bp.route("/room/<id>/message", methods=['POST'])
def send_message():
    return "<p>Hello, World!</p>"