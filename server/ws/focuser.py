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

from utils.i18n import _
from ..logging import logger ,return_error,return_success,return_warning

class WSFocuser(object):
    """
        Websocket focuser interface
    """

    def __init__(self,ws) -> None:
        """
            Initial a new WSFocuser
            Args : None
            Returns : None
        """
        self.device = None
        self.ws = ws
        self.thread = None

    def __del__(self) -> None:
        """
            Delete a WSFocuser
            Args : None
            Returns : None
        """

    def __str__(self) -> str:
        """
            Returns the name of the WSFocuser class
            Args : None
            Returns : None
        """
        return self.__class__.__name__

    async def connect(self , params = {}) -> None:
        """
            Async connect to the focuser 
            Args : 
                params : dict
                    type : str # ascom or indi
                    device_name : str
                    host : str # both indi and ascom default is "127.0.0.1"
                    port : int # for indi port is 7624 , for ascom port is 11111
            Returns : dict
                info : dict # BasicaFocuserInfo object
        """
        if self.device is not None:
            logger.info(_("Disconnecting from existing focuser ..."))
            self.disconnect()

        _type = params.get('type')
        _device_name = params.get('device_name')

        if _type is None or _device_name is None:
            logger.error(_("Type or device name must be specified"))
            return return_error(_("Type or device name must be specified"))
        
        if _type == "indi":
            """from server.api.indi.focuser import INDIFocuserAPI
            self.device = INDIFocuserAPI()"""
        elif _type == "ascom":
            from server.api.ascom.focuser import AscomFocuserAPI
            self.device = AscomFocuserAPI()
        else:
            logger.error(_("Unknown device type : {}").format(_type))
            return return_error(_("Unknown device type"))

        return self.device.connect(params=params)

    async def disconnect(self,params = {}) -> dict:
        """
            Async disconnect from the device
            Args : None
            Returns : dict
        """
        if self.device is None or not self.device.info._is_connected:
            logger.warning(_("Focuser is not connected , please do not execute disconnect command"))
            return return_error(_("Focuser is not connected"))
        
        return self.device.disconnect()

    async def reconnect(self,params = {}) -> dict:
        """
            Async reconnect to the device
            Args : None
            Returns : dict
                info : dict # just like connect()
            NOTE : This function is just allowed to be called when the focuser had already connected
        """
        if self.device is None or not self.device.info._is_connected:
            logger.warning(_("Focuser is not connected , please do not execute reconnect command"))
            return return_error(_("Focuser is not connected"))

        return self.device.reconnect()

    async def scanning(self,params = {}) -> dict:
        """
            Async scanning all of the devices available
            Args : None
            Returns : dict
                list : list # a list of focusers available
        """
        if self.device is not None or self.device.info._is_connected:
            logger.warning(_("Focuser had already been connected , please do not execute scanning command"))
            return return_error(_("Focuser has already been connected"))

        return self.device.scanning()

    async def polling(self,params = {}) -> dict:
        """
            Async polling method to get the newest focuser information
            Args : None
            Returns : dict
                info : dict # usually generated from get_dict() function
        """
        if self.device is not None or self.device.info._is_connected:
            logger.warning(_("Focuser is not connected , please do not execute polling command"))
            return return_error(_("Focuser is not connected"))

        return self.device.polling()

    # #############################################################
    #
    # Following methods are used to control the focuser
    #
    # #############################################################

    # #############################################################
    # Current position
    # #############################################################

    async def get_current_position(self,params = {}) -> dict:
        """
            Get the current position of the focuser
            Args : None
            Returns : dict
                position : int
        """

    # #############################################################
    # Move
    # #############################################################

    async def move_step(self,params = {}) -> dict:
        """
            Move in or out in a distance of the specified step
            Args : 
                params : dict
                    step : int
            Returns : dict
        """

    async def move_to(self,params = {}) -> dict:
        """
            Move to a specific position
            Args :
                params : dict
                    position : int
            Returns : dict
        """

    async def get_move_status(self,params = {}) -> dict:
        """
            Get the status of movement
            Args : None
            Returns : dict
                status : bool # True if the focuser is moving
                position : int # current position
        """

    async def get_move_result(self,params = {}) -> dict:
        """
            Get the result of movement
            Args : None
            Returns : dict
                position : int # current position
        """

    # #############################################################
    # Temperature
    # #############################################################

    async def get_temperature(self , params = {}) -> dict:
        """
            Get the current temperature of the focuser
            Args : None
            Returns : dict
                temperature : float
            NOTE : This function need focuser supported
        """