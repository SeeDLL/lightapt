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

from time import sleep
from requests import exceptions
from server.basic.focuser import BasicFocuserAPI,BasicFocuserInfo
from libs.alpyca.focuser import Focuser
from libs.alpyca.exceptions import (DriverException,
                                        NotConnectedException,
                                        NotImplementedException,
                                        InvalidValueException,
                                        InvalidOperationException)

from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

from json import dumps
from os import mkdir, path

class AscomFocuserAPI(BasicFocuserAPI):
    """
        ASCOM Focuser API via alpyca
    """

    def __init__(self) -> None:
        """
            Construct a new ASCOM Focuser object
            Args : None
            Returns : None
        """
        self.info = BasicFocuserInfo()
        self.device = None

    def __del__(self) -> None:
        """
            Delete the device instance
            Args : None
            Returns : None
        """
        if self.info._is_connected:
            self.disconnect()
    
    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM focuser | 连接ASCOM电调
            Args: 
                host: str # default is "127.0.0.1",
                port: int # default is 11111,
                device_number : int # default is 0
            Returns:
                status : int,
                message : str,
                params : 
                    info : BasicFocuserInfo object
        """
        # Check if the focuser had already been connected , if true just return the current status
        if self.info._is_connected or self.device is not None:
            log.logw(_("Focuser is connected, please do not execute connect command again"))
            return log.return_warning(_("Focuser is connected"),{"info":self.info.get_dict()})
        # Check if the parameters are correct
        host = params.get('host')
        port = params.get('port')
        device_number = params.get('device_number')
        # If the host or port is null
        if host is None or port is None or device_number is None:
            log.logw(_("Host and port must be specified"))
            return log.return_warning(_("Host or port or device_number is None"),{})
        # Trying to connect to the specified focuser
        try:
            self.device = Focuser(host + ":" + str(port), device_number)
            self.device.Connected = True
        except DriverException as e:
            log.loge(_("Faild to connect to device on {}:{} : {}").format(host,port,e))
            return log.return_error(_("Failed to connect to device"),{"error" : e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error while connecting to focuser"),{"error" : e})
        log.log(_("Connected to device successfully"))
        res = self.get_configration()
        if res.get('status') != 0:
            return log.return_error(_(f"Failed tp load focuser configuration"),{})
        self.info._is_connected = True
        self.info._type = "ascom"
        return log.return_success(_("Connect to focuser successfully"),{"info":res.get("info")})

    def disconnect(self) -> dict:
        """
            Disconnect from ASCOM focuser | 断链
            Args: None
            Returns: 
                status : int,
                message : str,
                params : None
            NOTE : This function must be called before destory all server
        """
        if not self.info._is_connected or self.device is None:
            log.logw(_("Focuser is not connected, please do not execute disconnect command"))
            return log.return_warning(_("Focuser is not connected"),{})
        try:
            self.device.Connected = False
        except DriverException as e:
            log.loge(_("Faild to disconnect from device , error : {}").format(e))
            return log.return_error(_(f"Failed to disconnect from device"),{"error" : e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_(f"Network error"),{"error" : e})
        self.device = None
        self.info._is_connected = False
        log.log(_("Disconnected from focuser successfully"))
        return log.return_success(_("Disconnect from focuser successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to ASCOM focuser | 重连
            Args: None
            Returns: 
                status : int,
                message : str,
                params : dict
                    info : BasicFocuserInfo object
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_("Focuser is not connected, please do not execute reconnect command"))
            return log.return_warning(_("Focuser is not connected"),{}) 
        try:
            self.device.Connected = False
            sleep(1)
            self.device.Connected = True
        except DriverException as e:
            log.loge(_("Faild to reconnect to device, error : {}").format(e))
            return log.return_error(_("Failed to reconnect to device"),{"error" : e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error" : e})
        log.log(_("Reconnect focuser successfully"))
        self.info._is_connected = True
        return log.return_success(_("Reconnect focuser successfully"),{"info" : self.info.get_dict()})

    def scanning(self) -> dict:
        """
            Scan the focuser | 扫描电调
            Args: None
            Returns: 
                status : int,
                message : str,
                params : 
                    focuser : list
        """

    def polling(self) -> dict:
        """
            Polling for ASCOM focuser
            Args: None
            Returns: 
                status : int,
                message : str,
                params : 
                    info : BasicFocuserInfo object
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_("Focuser is not connected, please do not execute polling command"))
            return log.return_warning(_("Focuser is not connected"),{})
        res = self.info.get_dict()
        log.logd(_(f"New focuser info : {res}"))
        return log.return_success(_("Focuser's information is refreshed"),{"info":res})

    def get_configration(self) -> dict:
        """
            Get focuser infomation | 获取电调信息
            Args: None
            Returns: 
                status : int,
                message : str,
                params : 
                    info : BasicFocuserInfo object
        """
        try:
            self.info._name = self.device.Name
            log.logd(_("Focuser name : {}").format(self.info._name))
            self.info._id = self.device._client_id
            log.logd(_("Focuser ID : {}").format(self.info._id))
            self.info._description = self.device.Description
            log.logd(_("Focuser description : {}").format(self.info._description))
            self.info._ipaddress = self.device.address
            log.logd(_("Focuser IP address : {}").format(self.info._ipaddress))
            self.info._api_version = self.device.api_version
            log.logd(_("Focuser API version : {}").format(self.info._api_version))

            # Get infomation about the focuser temperature ability
            self.info._can_temperature = self.device.TempCompAvailable
            log.logd(_(f"Can focuser get temperature: {self.info._can_temperature}"))
            if self.info._can_temperature:
                try:
                    self.info._temperature = self.device.Temperature
                    log.logd(_(f"Focuser current temperature : {self.info._temperature}°C"))
                except NotImplementedException as e:
                    log.loge(_(f"Failed to get current temperature , error: {e}"))
                    self.info._can_temperature = False
            else:
                self.info._temperature = -256

            # Get the max step the focuser can move to , this is for focuser safety purposes

            self.info._current_position = self.device.Position
            log.logd(_("Focuser Current Position: {}").format(self.info._current_position))
            self.info._max_steps = self.device.MaxStep
            log.logd(_("Focuser Max Step : {}").format(self.info._max_steps))
            self.info._max_increment = self.device.MaxIncrement
            log.logd(_("Focuser Max Increment : {}").format(self.info._max_increment))

            # Get the current position of the focuser 

            self.info._current_position = self.device.Position
            log.logd(_("Current Position : {}").format(self.info._current_position))
            self.info._step_size = self.device.StepSize
            log.logd(_("Step Size : {}").format(self.info._step_size))
        
        except NotImplementedException as e:
            log.loge(_("Focuser is not supported : {}").format(str(e)))
            return log.return_error(_("Focuser is not supported"),{"error":str(e)})
        except NotConnectedException as e:
            log.loge(_("Focuser is not connected : {}").format(e))
            return log.return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Drvier error : {}").format(e))
            return log.return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error":e})
        log.log(_("Get focuser configuration successfully"))
        return log.return_success(_("Get focuser configuration successfully"),{"info" : self.info.get_dict()})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of focuser
            Args : None
            Return : 
                status : int,
                message : str,
                params : None
        """
        _p = path.join
        _path = _p("config",_p("focuser",self.info._name+".json"))
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","focuser")):
            mkdir(_p("config","focuser"))
        self.info._configration = _path
        with open(_path,mode="w+",encoding="utf-8") as file:
            file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
        log.log(_("Save focuser information successfully"))
        return log.return_success(_("Save focuser information successfully"),{})

    # #################################################################
    #
    # The following functions are used to control the focuser (all is non-blocking)
    #
    # #################################################################

    def move_to(self, params: dict) -> dict:
        """
            Let the focuser move to the specified position
            Args : 
                params : dict
                    position : int # position of the target
            Returns :
                status : int
                message : str
                params : dict
                    position : int # position of the result
        """
        if not self.info._is_connected or self.device is None:
            log.loge(_("Focuser is not connected"))
            return log.return_error(_("Focuser is not connected"),{})
        if self.info._is_moving:
            log.loge(_("Focuser is moving , please wait for a moment"))
            return log.return_warning(_("Focuser is moving"),{})
        
        position = params.get("position")
        if position is None:
            log.loge(_("Target position is required , but given position is a null value"))
            return log.return_error(_("Target position is required"),{})
        
        if not isinstance(position,int) or not 0 <= position <= self.info._max_steps:
            log.loge(_("Please provide a valid position value"))
            return log.return_error(_("Position is not a valid value"),{})

        try:
            self.device.Move(Position=position)
        except InvalidValueException as e:
            log.loge(_("Invalid position value : {}").format(e))
            return log.return_error(_("Invalid position value"),{"error":e})
        except DriverException as e:
            log.loge(_("Driver error: {}").format(e))
            return log.return_error(_("Driver error: {}"),{"error":e})
        except NotConnectedException as e:
            log.loge(_("Focuser is not connected : {}").format(e))
            return log.return_error(_("Focuser is not connected"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error: {}").format(e))
            return log.return_error(_("Network error: {}"),{"error":e})

        log.log(_("Focuser started moving operation successfully"))
        self.info._is_moving = True
        return log.return_success(_("Focuser started operation successfully"),{})

    def move_step(self, params: dict) -> dict:
        """
            Move to position which add a specified steps to the current position
            Args : 
                params : dict
                    step : int # step size
            Returns :
                status : int
                message : str
                params : None
        """
        if not self.info._is_connected or self.device is None:
            log.loge(_("Focuser is not connected"))
            return log.return_error(_("Focuser is not connected"),{})

        if self.info._is_moving:
            log.loge(_("Focuser is moving"))
            return log.return_error(_("Focuser is moving"),{})

        step = params.get("step")

        if step is None or not isinstance(step,int):
            log.loge(_("Step size is required , but now it is not available"))
            return log.return_error(_("Step size is required , but now it is not available"),{})

        if step > self.info._max_increment or not 0 <= self.info._current_position + step <= self.info._max_steps:
            log.loge(_("Given step  is out of range and may cause the focuser broken"))
            return log.return_error(_("Given step is out of range and may cause the focuser broken"),{})

        try:
            self.device.Move(Position=self.info._current_position+step)
        except InvalidValueException as e:
            log.loge(_("Invalid step value : {}").format(e))
            return log.return_error(_("Invalid step value"),{"error":e})
        except InvalidOperationException as e:
            log.loge(_("Invalid operation value"),{"error":e})
            return log.return_error(_("Invalid operation value"),{"error":e})
        except NotConnectedException as e:
            log.loge(_("Focuser is not connected"),{"error":e})
            return log.return_error(_("Focuser is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Driver error : {}").format(e))
            return log.return_error(_("Focuser is not connected"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error":e})
        
        self.info._is_moving = True
        log.log(_("Focuser started move operation successfully"))
        return log.return_success(_("Focuser started move operation successfully"),{})

    def abort_move(self):
        """
            Abort current move operation
            Args : None
            Returns :
                status : int 
                message : str
                params : dict
                    position : int # current position after abort operation
        """
        if not self.info._is_connected or self.device is None:
            log.loge(_("Focuser is not connected"))
            return log.return_error(_("Focuser is not connected"),{})
        
        if not self.info._is_moving:
            log.loge(_("Focuser is not moving , please do not execute abort operation"))
            return log.return_error(_("Focuser is not moving"),{})

        try:
            self.device.Halt()
            sleep(0.5)
            if not self.device.IsMoving:
                self.info._is_moving = False
        except NotImplementedException as e:
            log.loge(_("Failed to abort focuser : {}").format(e))
            return log.return_error(_("Failed to abort focuser"),{"error":e})
        except NotConnectedException as e:
            log.loge(_("Focuser is not connected : {}").format(e))
            return log.return_error(_("Focuser is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Driver error : {}").format(e))
            return log.return_error(_("Driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error: {}").format(e))
            return log.return_error(_("Network error"),{"error":e})
            
        log.log(_("Abort focuser move operation successfully"))
        return log.return_success(_("Abort focuser move operation successfully"),{"position" : self.device.Position})
    
    def get_movement_status(self) -> dict:
        """
            Get the status of the current move operation
            Args : None
            Returns : 
                status : int
                message : str
                params : dict
                    status : int # status of the operation
                    position : int # position of the current position
        """
        if not self.info._is_connected or self.device is None:
            log.loge(_("Focuser is not connected"))
            return log.return_error(_("Focuser is not connected"),{})

        if not self.info._is_moving:
            log.loge(_("Focuser is not moving"))
            return log.return_error(_("Focuser is not moving"),{})

        try:
            status = self.device.IsMoving
            position = self.device.Position
        except NotImplementedException as e:
            log.loge(_("Failed to get status of the focuser operation : {}").format(e))
            return log.return_error(_("Failed to get status of the operation"),{"error":e})
        except NotConnectedException as e:
            log.loge(_("Focuser is not connected : {}").format(e))
            return log.return_error(_("Failed to get status of the operation"),{"error":e})
        except DriverException as e:
            log.loge(_("Driver error : {]").format(e))
            return log.return_error(_("Driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error":e})

        log.logd(_("Get the focuser status successfully : position : {}").format(position))

        return log.return_success(_("Get focuser status successfully"),{"status" : status,"position":position})

    def get_temperature(self) -> dict:
        """
            Get the current temperature of the focuser
            Args : None
            Returns : dict
                status : int
                message : str
                params : dict
                    temperature : float
            NOTE : This function needs focuser supported
        """
        # Check if the focuser is connected
        if not self.info._is_connected or self.device is None:
            log.loge(_("Focuser is not connected"))
            return log.return_error(_("Focuser is not connected"),{})

        if not self.info._can_temperature:
            log.loge(_("Focuser is not supported to get temperature"))
            return log.return_error(_("Focuser is not supported to get temperature"))

        try:
            self.info._temperature = self.device.Temperature
        except NotImplementedException as e:
            log.loge(_("Focuser is not supported to get temperature : {}").format(e))
            return log.return_error(_("Focuser is not supported to get temperature"),{"error":e})
        except NotConnectedException as e:
            log.loge(_("Focuser is not connected : {}").format(e))
            self.info._is_connected = False
            return log.return_error(_("Focuser is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Driver error : {}").format(e))
            return log.return_error(_("Driver error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error: {}").format(e))
            return log.return_error(_("Network error"),{"error":e})

        log.logd(_("Current Focuser Temperature : {}").format(self.info._temperature))

        return log.return_success(_("Get focuser temperature successfully"),{"temperature":self.info._temperature})

    