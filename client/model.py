
from dataclasses import dataclass
import logging
from typing import List
from client.api import Api


@dataclass
class Message:
    id: int
    author_id: int
    author_name: str
    created_at: str
    text: str

@dataclass
class Room:
    id: int
    name: str

class HydratedRoom:
    def __init__(self, api: Api, room: Room) -> None:
        self.room = room
        
        message_list = api.get_messages(room.id)
        self.messages: List[Message] = []
        for m in message_list:
            self.messages.append(Message(**m))

    def get_message(self, message_id: int) -> Message:
        for m in self.messages:
            if m.id == message_id:
                return m
        return None

    def update_messages(self, new_message: Message):
        if not self.get_message(new_message.id):
            self.messages.append(new_message)
            self.messages.sort(key=lambda m: m.id)
        else:
            logging.info(f"Message already on the list: {new_message=}")


class ChatModel:
    def __init__(self, api: Api) -> None:
        self.api = api
        room_list = api.list_rooms()
        self.rooms: List[HydratedRoom] = []
        for r in room_list:
            self.rooms.append(HydratedRoom(self.api, Room(**r)))

    def get_room(self, room_id) -> HydratedRoom:
        for r in self.rooms:
            if r.room.id == room_id:
                return r
        return None
    
    def update_rooms(self, new_room: Room):
        if not self.get_room(new_room.id):
            self.rooms.append(HydratedRoom(self.api, new_room))
            self.rooms.sort(key=lambda r: r.room.id)
        else:
            logging.info(f"Room already on the list: {new_room=}")
