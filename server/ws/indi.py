# coding=utf-8

"""

Copyright(c) 2023 Gao Le

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.
You should have received a copy of the GNU Library General Public License
along with this library; see the file COPYING.LIB.  If not, write to
the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.

"""

import json
import tornado.web
from ..api.indi import ws_indi_worker

# #################################################################
# INDI Debug 
# #################################################################

class INDIDebugWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin: str) -> bool:
        return True

    def open(self):
        print("Debugging WS opened")

    def on_message(self, message):
        commands = message.split(' ')
        self.write_message(ws_indi_worker.do_debug_command(commands))

    def on_close(self):
        print("Debugging WSclosed")

# #################################################################
# INDI Fifo device (device start or stop)
# #################################################################

class INDIFIFODeviceStartStop(tornado.web.RequestHandler):
    async def get(self, start_or_stop, device_type, device_name):
        # print(start_or_stop, device_type, device_name)
        if start_or_stop == 'start':
            ret_bool = ws_indi_worker.indi_fifo_start_device(device_type, device_name, True)
        elif start_or_stop == 'stop':
            ret_bool = ws_indi_worker.indi_fifo_start_device(device_type, device_name, False)
        else:
            return self.write('Wrong Command!')
        if ret_bool:
            self.write('Got!')
        else:
            self.write('Wrong device name!')

class INDIFIFOGetAllDevice(tornado.web.RequestHandler):
    async def get(self):
        all_devices = ws_indi_worker.get_all_devices()
        self.write(json.dumps(all_devices))

# #################################################################
# INDI Client
# #################################################################

class INDIClientWebSocket(tornado.websocket.WebSocketHandler):
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

class INDIDebugHtml(tornado.web.RequestHandler):
    """
        INDI Debug page container
    """
    def get(self):
        self.render("idebug.html")