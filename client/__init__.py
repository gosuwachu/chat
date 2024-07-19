import urwid
import requests
import argparse
import json

# Define API URL
API_URL = "http://127.0.0.1:5000"

# Global variables to store user and room states
current_user = None
current_room = None
messages_list = None
message_container = None
message_edit = None
rooms_list = None

# Handle command-line arguments
parser = argparse.ArgumentParser(description="TUI Chat Client")
parser.add_argument("username", type=str, help="The username for the chat client")
args = parser.parse_args()
username = args.username

def handle_api_error(response):
    if response.status_code != 200:
        try:
            error_message = response.json().get('error', 'Unknown error occurred.')
        except json.JSONDecodeError:
            error_message = 'Unknown error occurred.'
        raise Exception(error_message)
    return response.json()

# Functions for API interactions
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

# Initialize the current user
def initialize_user(username):
    global current_user
    current_user = create_user(username)
    
# Main UI Components
def exit_program(button):
    raise urwid.ExitMainLoop()

def update_messages_list(room_id):
    try:
        messages = get_messages(room_id)
        messages_texts = [format_message(msg) for msg in messages]
        messages_text = "\n".join(messages_texts)
    except Exception as e:
        messages_text = f"Error: {str(e)}"
    
    messages_list.set_text(messages_text)

def format_message(msg):
    if msg['author_name'] == 'system':
        return f"[{msg['created_at']}] {msg['text']}"
    else:
        return f"[{msg['created_at']}] {msg['author_name']}: {msg['text']}"

def on_room_select(button, room_id):
    select_room(room_id)

def select_room(room_id):
    global current_room
    current_room = room_id
    try:
        try:
            join_room(room_id, current_user['id'])
        except:
            pass
        update_messages_list(room_id)
    except Exception as e:
        messages_list.set_text(f"Error: {str(e)}")

def on_leave_room(button, room_id):
    global current_room
    try:
        leave_room(room_id, current_user['id'])
        current_room = None
        messages_list.set_text("Left the room.")
    except Exception as e:
        messages_list.set_text(f"Error: {str(e)}")

def on_create_room(edit_widget):
    room_name = edit_widget.get_edit_text()
    if room_name:
        try:
            room = create_room(room_name)
            refresh_room_list()
            select_room(room['id'])
        except Exception as e:
            messages_list.set_text(f"Error: {str(e)}")

def on_send_message(button=None):
    if current_room and current_user:
        text = message_edit.edit_text
        if text:
            try:
                send_message(current_room, current_user['id'], text)
                message_edit.edit_text = ""
                message_container.set_scrollpos(-1)
                update_messages_list(current_room)
            except Exception as e:
                messages_list.set_text(f"Error: {str(e)}")

class MessageEdit(urwid.Edit):
    def keypress(self, size, key):
        if key == 'enter':
            on_send_message()
        else:
            return super().keypress(size, key)

class CreateRoomEdit(urwid.Edit):
    def keypress(self, size, key):
        if key == 'enter':
            on_create_room(self)
        else:
            return super().keypress(size, key)

def refresh_room_list():
    try:
        rooms = list_rooms()
        room_buttons = [
            urwid.Columns([
                ('weight', 1, urwid.Button(room['name'], on_press=on_room_select, user_data=room['id'])),
                ('pack', urwid.Button("X", on_press=on_leave_room, user_data=room['id']))
            ]) for room in rooms]
    except Exception as e:
        room_buttons = [urwid.Text(f"Error: {str(e)}")]
    rooms_list.body = urwid.SimpleFocusListWalker(room_buttons)

def main_layout():
    global messages_list, message_edit, message_container, rooms_list

    rooms_list = urwid.ListBox(urwid.SimpleFocusListWalker([]))
    refresh_room_list()
    
    messages_list = urwid.Text("Select a room to see messages")
    message_container = urwid.Scrollable(messages_list)

    message_edit = MessageEdit("> ")

    room_create_edit = CreateRoomEdit("> ")
    room_create_widget = urwid.Pile([room_create_edit])

    rooms_column = urwid.Pile([
        ('weight', 1, urwid.LineBox(rooms_list, title="Rooms")),
        ('pack', urwid.LineBox(room_create_widget, title="New Room"))
    ], focus_item=0)

    messages_column = urwid.Pile([
        ('weight', 1, urwid.LineBox(message_container, title="Messages")), 
        ('pack', urwid.LineBox(message_edit, title="Send"))
    ], focus_item=1)

    columns = urwid.Columns([('weight', 1, rooms_column), ('weight', 3, messages_column)])
    
    return columns

# Initialize the TUI application
initialize_user(username)
top_widget = main_layout()
main_loop = urwid.MainLoop(top_widget, unhandled_input=lambda key: exit_program(None) if key in ('q', 'Q') else None)
main_loop.run()
