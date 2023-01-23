import tornado.websocket
import json
from ..IndiInterface import ws_indi_worker


class DebuggingWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return True

    def open(self):
        print("Debugging WS opened")

    def on_message(self, message):
        commands = message.split(' ')
        self.write_message(ws_indi_worker.do_debug_command(commands))

    def on_close(self):
        print("Debugging WSclosed")
