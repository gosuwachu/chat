import json
import requests

# Define API URL
API_URL = "http://127.0.0.1:5000"


def handle_api_error(response):
    if response.status_code != 200:
        try:
            error_message = response.json().get('error', 'Unknown error occurred.')
        except json.JSONDecodeError:
            error_message = 'Unknown error occurred.'
        raise Exception(error_message)
    return response.json()


def create_user(name):
    response = requests.post(f"{API_URL}/user/create", json={"name": name})
    return handle_api_error(response)


def list_users():
    response = requests.get(f"{API_URL}/user")
    return handle_api_error(response)


def create_room(name):
    response = requests.post(f"{API_URL}/room/create", json={"name": name})
    return handle_api_error(response)


def list_rooms():
    response = requests.get(f"{API_URL}/room")
    return handle_api_error(response)


def join_room(room_id, user_id):
    response = requests.post(f"{API_URL}/room/{room_id}/join/{user_id}")
    return handle_api_error(response)


def leave_room(room_id, user_id):
    response = requests.post(f"{API_URL}/room/{room_id}/leave/{user_id}")
    return handle_api_error(response)


def list_participants(room_id):
    response = requests.get(f"{API_URL}/room/{room_id}/participants")
    return handle_api_error(response)


def send_message(room_id, author_id, text):
    response = requests.post(f"{API_URL}/room/{room_id}/user/{author_id}/message", json={"text": text})
    return handle_api_error(response)


def get_messages(room_id):
    response = requests.get(f"{API_URL}/room/{room_id}/message")
    return handle_api_error(response)