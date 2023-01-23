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

# #################################################################
#
# This client is not directly connecting to INDI but our own server
#
# #################################################################

import threading


import libs.wsclient as ws

from utils.i18n import _
from utils.lightlog import lightlog
logger = lightlog(__name__)

class WsINDIClient(object):
    """
        Websocket INDI wrapper server API
    """

    def __init__(self) -> None:
        """
            Initialize a new INDI client instance
            Args : None
            Returns : None
        """
        self.client = ws.WebSocketApp("localhost:7999",
                    on_data = self.on_data,
                    on_close = self.on_close,
                    on_error = self.on_error,
                    on_open = self.on_open,
                    on_message = self.on_message,
                )
        self.thread = threading.Thread(target=self.client.run_forever)
        try:
            self.thread.daemon = True
        except:
            self.thread.setDaemon(True)
        self.thread.start()

    def __del__(self) -> None:
        """
            Delete the connection object
        """

    def on_open(self,_ws : ws.WebSocketApp) -> None:
        """
            Event handler for the on_open event
            Args : 
                _ws : ws.WebSocketApp instance
            Returns : None
        """
        logger.log(_("Established websocket connection with client"))

    def on_close(self,_ws : ws.WebSocketApp , close_status_code, close_msg) -> None:
        """
            Event handler for the on_close event
            Args :
                _ws : ws.WebSocketApp instance
                close_status_code : int
                close_msg : str
            Returns : None
        """
        logger.log(_("Close the websocket connection"))

    def on_error(self,_ws : ws.WebSocketApp , err) -> None:
        """
            Event handler for the on_error event
            Args :
                _ws : ws.WebSocketApp instance
                err : str
            Returns : None
        """
        logger.loge(_("Some error occurred : {}").format(err))

    def on_message(self,_ws : ws.WebSocket , message) -> None:
        """
            Event handler for the on_message event
            Args :
                _ws : ws.WebSocketApp instance
                message : str
            Returns : None
        """
        def parser_json(message : str) -> None:
            """
                JSON data parser
                Args : 
                    message : str
                Returns : None
            """

        logger.logd(_("Received message : {}").format(message))
        threading.Thread(target=parser_json(message=message)).start()

    def on_data(self,_ws : ws.WebSocket , data) -> None:
        """
            Event handler for the on_data event
            Args :
                _ws : ws.WebSocket instance
                data : bytes
            Returns : None
        """
