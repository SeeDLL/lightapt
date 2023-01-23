# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <lightapt.com>

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

# System Library
from json import JSONDecodeError, dumps
from secrets import randbelow
import threading
from time import sleep
# Third Party Library

# Built-in Library

import server.config as c

from utils.i18n import _
from utils.lightlog import lightlog
logger = lightlog(__name__)

class WsFilterwheelMessage(object):
    """
        A websocket message container
    """
    NotConnected = _("Filterwheel is not connected")
    IsSlewing = _("Filterwheel is slewing")

fmessage = WsFilterwheelMessage()

class WsFilterwheelInterface(object):
    """
        Websocket Filterwheel interface\n
        Needed API :
            move_step(params : dict) -> dict
                params : dict
                    step : int
            move_to(params : dict) -> dict
                params : dict
                    position : int
            abort_movement() -> dict
            get_movement_status() -> dict
            get_temperature() -> dict
    """

    def __init__(self) -> None:
        """
            Initialize the websocket filterwheel interface object
            Args : None
            Returns : None
        """
        self.device = None
        self.thread = None

    def __del__(self) -> None:
        """
            Close the websocket filterwheel interface object
            Args : None
            Returns : None
        """
        if self.device.info._is_connected:
            self.device.disconnect()

    def __str__(self) -> str:
        """
            Return the string representation of the websocket filterwheel interface object
            Args : None
            Returns : Filterwheel string
        """
        return """
            Basic websocket filterwheel interface
            version : 1.0.0 indev
        """

    def on_send(self, message : dict) -> bool:
        """
            Send message to client | 将信息发送至客户端
            Args:
                message: dict
            Returns: True if message was sent successfully
            Message Example:
                status : int ,
                message : str,
                params : dict
        """
        if not isinstance(message, dict) or message.get("status") is None or message.get("message") is None:
            logger.loge(_("Unknown format of message"))
            return False
        try:
            c.ws.send_message_to_all(dumps(message))
        except JSONDecodeError as exception:
            logger.loge(_(f"Failed to parse message into JSON format , error {exception}"))
            return False
        return True 

    def remote_connect(self,params : dict) -> None:
        """
            Connect to the filterwheel | 连接滤镜轮,在成功后获取滤镜轮信息并返回客户端
            Args : 
                params :
                    "host" : str # default is "localhost"
                    "port" : int # port of the INDI or ASCOM server
                    "type" : str # default is "indi"
                    "name" : str # name of the filterwheel , default is "CCD Simulator"
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the connection
                id : int # just a random number
                message : str # message of the connection
                params : info : BasicFilterwheelInfo object
        """
        r = {
            "event" : "RemoteConnect",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        # If the parameters are not specified
        if params is None:
            r["message"] = _("No parameters provided")
            if self.on_send(r) is False:
                logger.loge(_("Failed to send message while executing connect command"))
            return

        _host = params.get("host", "localhost")
        _port = int(params.get("port", 7624))
        _type = params.get("type", "indi")
        _name = params.get("name", "Filterwheel Simulator")

        param = {
            "host" : _host,
            "port" : _port
        }
        # If the filterwheel had already connected
        if self.device is not None and self.device.info._is_connected:
            logger.logw(_("Filterwheel is connected"))
            r["status"] = 2
            r["message"] = "Filterwheel is connected"
            r["params"]["info"] = self.device.info.get_dict()
            if self.on_send(r) is False:
                logger.loge(_("Failed to send message while executing connect command"))
            return
        # Check if the type of the filterwheel is supported
        if _type in ["indi","ascom"]:
            # Connect to ASCOM filterwheel , the difference between INDI is the devie_number
            if _type == "ascom":    
                from server.api.ascom.filterwheel import AscomFilterwheelAPI as ascom_filterwheel
                self.device = ascom_filterwheel()
                param["device_number"] = 0
            # Connect to INDI filterwheel , the name of the device is needed
            elif _type == "indi":
                """from server.driver.filterwheel.indi import INDIFilterwheelAPI as indi_filterwheel
                self.device = indi_filterwheel()"""
                param["name"] = _name
            # Trying to connect the filterwheel
            res = self.device.connect(params=param)
            if res.get('status') != 0:
                logger.loge(_(f"Failed to connect to {_host}:{_port}, error {res.get('status')}"))
                # If there is no error infomation
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except KeyError:
                    pass
            else:
                r["status"] = 0
                r["params"]["info"] = res.get("params").get("info")
            r['message'] = res.get("message")
        # Unkown type of the filterwheel
        else:
            logger.loge(_(f"Unknown type {_type}"))
            r["message"] = _("Unknown type")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing connect command"))

    def remote_disconnect(self):
        """
            Disconnect from the filterwheel
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the disconnection
                id : int # just a random number
                message : str # message of the disconnection
                params : None
        """
        r = {
            "event" : "RemoteDisconnect",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(fmessage.NotConnected)
            r["message"] = fmessage.NotConnected
        else:
            res = self.device.disconnect()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to disconnect from the filterwheel"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except KeyError:
                    pass
            else:
                r["status"] = 0
                logger.log(_("Disconnected from filterwheel successfully"))
            r["message"] = res.get('message')
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing disconnect command"))

    def remote_reconnect(self) -> None:
        """
            Reconnect to the filterwheel
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the reconnection
                id : int # just a random number
                message : str # message of the reconnection
                params : info : BasicFilterwheelInfo object
        """
        r = {
            "event" : "RemoteReconnect",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        if not self.device.info._is_connected:
            logger.loge(fmessage.NotConnected)
            r["message"] = fmessage.NotConnected
        else:
            res = self.device.reconnect()
            if res.get('status')!= 0:
                logger.loge(_(f"Failed to reconnect to the filterwheel"))
                try:
                    r["params"]["error"] = res.get('params').get('error')
                except KeyError:
                    pass
            else:
                r["status"] = 0
                r["params"]["info"] = res.get("params").get("info")
                logger.log(_("Reconnected to filterwheel successfully"))
            r["message"] = res.get("message")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing reconnect command"))

    def remote_scanning(self) -> None:
        """
            Scannings from the filterwheel
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the scanning
                id : int # just a random number
                message : str # message of the scanning
                params : list : a list of filterwheel name
        """
        r = {
            "event" : "RemoteScanning",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        res = self.device.scanning()
        if res.get('status')!= 0:
            logger.loge(_(f"Failed to scan from the filterwheel"))
            try:
                r["params"]["error"] = res.get('params').get('error')
                logger.log(_("Error : {}").format(r["params"]["error"]))
            except KeyError:
                pass
        else:
            r["status"] = 0
            r["params"]["list"] = res.get("params").get("list")
            logger.log(_("Scanning filterwheel successfully, found {} filterwheel").format(len(r["params"]["list"])))
        r["message"] = res.get("message")
    
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing scan command"))

    def remote_polling(self) -> None:
        """
            Polling newest message from the filterwheel
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the polling
                id : int # just a random number
                message : str # message of the polling
                params : dict
                    info : BasicFilterwheelInfo object
        """
        r = {
            "event" : "RemotePolling",
            "id" : randbelow(1000),
            "status" : 1,
            "message" : "",
            "params" : {}
        }
        res = self.device.polling()
        if res.get('status')!= 0:
            logger.loge(_(f"Failed to poll from the filterwheel"))
            try:
                r["params"]["error"] = res.get('params').get('error')
                logger.loge(_("Error : {}").format(r["params"]["error"]))
            except KeyError:
                pass
        else:
            r["status"] = 0
            r["params"]["info"] = res.get("params").get("info")
            logger.logd(_("Get filterwheel information : {}").format(r["params"]["info"]))
        r["message"] = res.get("message")
        if self.on_send(r) is False:
            logger.loge(_("Failed to send message while executing polling command"))

    # #################################################################
    #
    # Filterwheel control functions
    #
    # #################################################################

    def remote_slew_to(self,params : dict) -> None:
        """
            Remote slew to function
            Args :
                params : dict
                    position : int
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the polling
                id : int # just a random number
                message : str # message of the polling
                params : None
        """

    def remote_get_filter_list(self) -> None:
        """
            Remote get filter list of the offsets and names
            Args : None
            Returns : None
            ClientRetuen : 
                event : str # event name
                status : int # status of the polling
                id : int # just a random number
                message : str # message of the polling
                params : dict
                    offset : list
                    name : list
        """

    def remote_get_current_position(self) -> None:
        """
            Remote get current position of the filterwheel
            Args : None
            Returns : None
            ClientReturn:
                event : str # event name
                status : int # status of the polling
                id : int # just a random number
                message : str # message of the polling
                params : dict
                    position : int
        """