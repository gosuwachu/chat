from flask import Flask

app = Flask(__name__)

@app.route("/room/join")
def join_room():
    return "<p>Hello, World!</p>"

@app.route("/room/leave")
def leave_room():
    return "<p>Hello, World!</p>"

@app.route("/rooms")
def rooms():
    return "<p>Hello, World!</p>"

@app.route("/room/<id>/participants")
def room_participants():
    return "<p>Hello, World!</p>"

@app.route("/room/<id>/messages")
def get_messages():
    return "<p>Hello, World!</p>"

@app.route("/room/<id>/message")
def send_message():
    return "<p>Hello, World!</p>"
