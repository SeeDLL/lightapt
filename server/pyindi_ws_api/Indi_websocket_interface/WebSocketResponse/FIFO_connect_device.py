import tornado.web
from ..IndiInterface import ws_indi_worker
import json


class FIFODeviceStartStop(tornado.web.RequestHandler):
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


class FIFOGetAllDevice(tornado.web.RequestHandler):
    async def get(self):
        all_devices = ws_indi_worker.get_all_devices()
        self.write(json.dumps(all_devices))
