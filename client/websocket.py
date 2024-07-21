from asyncio import sleep
import json
import logging
import websockets
from client.app import Client
from client.model import Message, Room


async def websocket_connection(app: Client):
    uri = "ws://localhost:6789"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logging.info("Connected to websocket server.")

                connect_message = json.dumps({'connect': {'user_id': app.current_user['id']}})
                
                logging.info("Send connect message.")
                await websocket.send(connect_message)
                
                async for event in websocket:
                    event = json.loads(event)
                    logging.info(f"Received: {event=}")
                    if 'created_room' in event:
                        room = event['created_room']
                        app.chat_model.update_rooms(Room(**room))
                        app.update_room_list()
                    elif 'message' in event:
                        room_id = event['message'].pop('room_id')
                        app.chat_model.get_room(room_id).update_messages(Message(**event['message']))
                        app.update_messages_list(room_id)
        except Exception as ex:
            logging.info(f"Websocket exception: {ex}")
            await sleep(0.5)
