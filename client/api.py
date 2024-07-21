import json
import requests

def handle_api_error(response):
    if response.status_code != 200:
        try:
            error_message = response.json().get('error', 'Unknown error occurred.')
        except json.JSONDecodeError:
            error_message = 'Unknown error occurred.'
        raise Exception(error_message)
    return response.json()

class Api:
    def __init__(self, host) -> None:
        self.api_url = f"http://{host}:5000"

    def create_user(self, name):
        response = requests.post(f"{self.api_url}/user/create", json={"name": name})
        return handle_api_error(response)

    def list_users(self):
        response = requests.get(f"{self.api_url}/user")
        return handle_api_error(response)

    def create_room(self, name):
        response = requests.post(f"{self.api_url}/room/create", json={"name": name})
        return handle_api_error(response)

    def list_rooms(self):
        response = requests.get(f"{self.api_url}/room")
        return handle_api_error(response)

    def join_room(self, room_id, user_id):
        response = requests.post(f"{self.api_url}/room/{room_id}/join/{user_id}")
        return handle_api_error(response)

    def leave_room(self, room_id, user_id):
        response = requests.post(f"{self.api_url}/room/{room_id}/leave/{user_id}")
        return handle_api_error(response)

    def list_participants(self, room_id):
        response = requests.get(f"{self.api_url}/room/{room_id}/participants")
        return handle_api_error(response)

    def send_message(self, room_id, author_id, text):
        response = requests.post(f"{self.api_url}/room/{room_id}/user/{author_id}/message", json={"text": text})
        return handle_api_error(response)

    def get_messages(self, room_id):
        response = requests.get(f"{self.api_url}/room/{room_id}/message")
        return handle_api_error(response)
