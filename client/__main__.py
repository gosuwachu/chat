import urwid
import argparse
import asyncio
import logging

from client.api import Api
from client.app import Client
from client.websocket import websocket_connection

# Handle command-line arguments
parser = argparse.ArgumentParser(description="TUI Chat Client")
parser.add_argument("username", type=str, help="The username for the chat client")
parser.add_argument("--host", type=str, help="Host", default="127.0.0.1")
parser.add_argument("--port", type=str, help="Port", default="8088")
args = parser.parse_args()

username = args.username
host = args.host
port = args.port

def exit_program(button):
    raise urwid.ExitMainLoop()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(f"chat_client.log.{username}"),
])

api = Api(host, port)
app = Client(api, username)

event_loop = asyncio.get_event_loop()
urwid_event_loop = urwid.AsyncioEventLoop(loop=event_loop)

event_loop.create_task(websocket_connection(host, port, app))

main_loop = urwid.MainLoop(app.top_widget, unhandled_input=lambda key: exit_program(None) if key in ('q', 'Q') else None, event_loop=urwid_event_loop)
app.main_loop = main_loop

main_loop.run()
