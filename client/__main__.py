import urwid
import argparse
import asyncio
import logging

from client.app import Client
from client.websocket import websocket_connection

# Handle command-line arguments
parser = argparse.ArgumentParser(description="TUI Chat Client")
parser.add_argument("username", type=str, help="The username for the chat client")
args = parser.parse_args()
username = args.username

def exit_program(button):
    raise urwid.ExitMainLoop()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(f"chat_client.log.{username}"),
])

app = Client(username)

event_loop = asyncio.get_event_loop()
urwid_event_loop = urwid.AsyncioEventLoop(loop=event_loop)

event_loop.create_task(websocket_connection(app))

main_loop = urwid.MainLoop(app.top_widget, unhandled_input=lambda key: exit_program(None) if key in ('q', 'Q') else None, event_loop=urwid_event_loop)
app.main_loop = main_loop

main_loop.run()
