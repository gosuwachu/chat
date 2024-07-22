import asyncio
import sqlite3
import websockets
import redis.asyncio as redis
import json
import logging

def get_db():
    db = sqlite3.connect(
        'instance/chat.sqlite',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def remove_connection(connection_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM connection WHERE id = ?', (connection_id,))
    db.commit()
    db.close()

def add_connection(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT OR REPLACE INTO connection (user_id) VALUES (?)', (user_id, ))
    db.commit()
    connection_id = cursor.lastrowid
    db.close()
    return connection_id

async def listen_to_event_queue(user_id, connection_id, websocket: websockets.WebSocketClientProtocol):
    redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

    while True:
        entry = await redis_client.blpop(f'user:{user_id}', timeout=0.1)
        if entry:
            event = entry[1]
            logging.info(f"Sent message to user {user_id=} {connection_id=}: {event=}")
            await websocket.send(entry[1])
        else:
            await websocket.ping()

async def handle_connection(websocket: websockets.WebSocketClientProtocol):
    logging.info("New connection")
    connection_id = None
    try:
        # Receive connection message
        message = await websocket.recv()
        logging.info(f"Message: {message}")

        message_data = json.loads(message)

        if 'connect' in message_data:
            user_id = message_data['connect']['user_id']
            connection_id = add_connection(user_id)
        else:
            websocket.close()
            return
        
        logging.info(f"Connected: {user_id=} {connection_id=}")
        await listen_to_event_queue(user_id, connection_id, websocket)
    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if connection_id:
            logging.info(f"Disconnected: {connection_id=}")
            remove_connection(connection_id)
        else:
            logging.warn(f"No connection id!")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    start_server = websockets.serve(handle_connection, '0.0.0.0', 6789)
    logging.info("Started on ws://localhost:6789")

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
