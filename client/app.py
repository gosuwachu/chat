from typing import Callable
import urwid
from client.api import Api

from client.model import ChatModel, Message

class OnEnterEdit(urwid.Edit):
    def __init__(self, caption, on_enter: Callable) -> None:
        self.on_enter = on_enter
        super().__init__(caption)

    def keypress(self, size, key):
        if key == 'enter':
            self.on_enter()
        else:
            return super().keypress(size, key)

class Client:
    def __init__(self, api: Api, username) -> None:
        self.api = api
        self.current_user = None
        self.current_room = None
        self.main_loop = None

        self.initialize_user(username)
        self.chat_model = ChatModel(api)

        self.rooms_list = urwid.ListBox(urwid.SimpleFocusListWalker([]))
        self.update_room_list()
        
        self.messages_list = urwid.Text("Select a room to see messages")
        self.message_container = urwid.Scrollable(self.messages_list)

        self.message_edit = OnEnterEdit(f"{username}> ", lambda: self.on_send_message())

        self.room_create_edit = OnEnterEdit("> ", lambda: self.on_create_room())
        room_create_widget = urwid.Pile([self.room_create_edit])

        rooms_column = urwid.Pile([
            ('weight', 1, urwid.LineBox(self.rooms_list, title="Rooms")),
            ('pack', urwid.LineBox(room_create_widget, title="New Room"))
        ], focus_item=0)

        messages_column = urwid.Pile([
            ('weight', 1, urwid.LineBox(self.message_container, title="Messages")), 
            ('pack', urwid.LineBox(self.message_edit, title="Send"))
        ], focus_item=1)

        self.top_widget = urwid.Columns([('weight', 1, rooms_column), ('weight', 3, messages_column)])
    
    def initialize_user(self, username):
        self.current_user = self.api.create_user(username)

    def update_room_list(self):
        try:
            rooms = self.chat_model.rooms
            room_buttons = [
                urwid.Columns([
                    ('weight', 1, urwid.Button(r.room.name, on_press=self.on_room_select, user_data=r.room.id)),
                    ('pack', urwid.Button("X", on_press=self.on_leave_room, user_data=r.room.id))
                ]) for r in rooms]
        except Exception as e:
            room_buttons = [urwid.Text(f"Error: {str(e)}")]
        self.rooms_list.body = urwid.SimpleFocusListWalker(room_buttons)

        if self.main_loop:
            self.main_loop.draw_screen()
    
    def update_messages_list(self, room_id):
        try:
            messages = self.chat_model.get_room(room_id).messages
            messages_texts = [self.format_message(msg) for msg in messages]
            messages_text = "\n".join(messages_texts)
        except Exception as e:
            messages_text = f"Error: {str(e)}"
        
        self.messages_list.set_text(messages_text)
        self.message_container.set_scrollpos(-1)

        if self.main_loop:
            self.main_loop.draw_screen()

    def format_message(self, msg: Message):
        if msg.author_name == 'system':
            return f"[{msg.created_at}] {msg.text}"
        else:
            return f"[{msg.created_at}] {msg.author_name}: {msg.text}"

    def on_room_select(self, button, room_id):
        self.select_room(room_id)

    def select_room(self, room_id):
        self.current_room = room_id
        try:
            try:
                self.api.join_room(room_id, self.current_user['id'])
            except:
                pass
            self.update_messages_list(room_id)
        except Exception as e:
            self.messages_list.set_text(f"Error: {str(e)}")

    def on_leave_room(self, button, room_id):
        global current_room
        try:
            self.api.leave_room(room_id, self.current_user['id'])
            self.current_room = None
            self.messages_list.set_text("Left the room.")
        except Exception as e:
            self.messages_list.set_text(f"Error: {str(e)}")

    def on_create_room(self):
        room_name = self.room_create_edit.edit_text
        self.room_create_edit.edit_text = ""
        if room_name:
            try:
                self.api.create_room(room_name)
            except Exception as e:
                self.messages_list.set_text(f"Error: {str(e)}")

    def on_send_message(self, button=None):
        if self.current_room and self.current_user:
            text = self.message_edit.edit_text
            if text:
                try:
                    self.api.send_message(self.current_room, self.current_user['id'], text)
                    self.message_edit.edit_text = ""
                except Exception as e:
                    self.messages_list.set_text(f"Error: {str(e)}")