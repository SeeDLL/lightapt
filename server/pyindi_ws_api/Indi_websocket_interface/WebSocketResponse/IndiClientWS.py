import tornado.websocket
import json
from ..IndiInterface import ws_indi_worker


class IndiClientWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return True

    def open(self):
        print("Client Instruction WS opened")

    async def on_message(self, message):
        """
        :param message:{
            device_name
            instruction
            params
        }
        :return:
        """
        command_json = json.loads(message)
        return_struct = await ws_indi_worker.accept_instruction(
            command_json['device_name'],
            command_json['instruction'],
            command_json['params'],
            self
        )
        await self.write_message(json.dumps(return_struct))

    def on_close(self):
        print("Client Instruction WS  closed")