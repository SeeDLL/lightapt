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
from server.basic.filterwheel import BasicFilterwheelAPI,BasicFilterwheelInfo
from libs.alpyca.filterwheel import FilterWheel
from libs.alpyca.exceptions import (DriverException,
                                        NotConnectedException,
                                        InvalidValueException)

from utils.lightlog import lightlog
log = lightlog(__name__)

import gettext
_ = gettext.gettext

from json import dumps
from os import mkdir, path

class AscomFilterwheelAPI(BasicFilterwheelAPI):
    """
        ASCOM Filterwheel API
    """

    def __init__(self) -> None:
        """
            Initialize the ASCOM Filterwheel object
            Args : None
            Returns : None
        """
        self.info = BasicFilterwheelInfo()
        self.device = None

    def __del__(self) -> None:
        """
            Delete the ASCOM Filterwheel object
            Args : None
            Returns : None
        """
        if self.info._is_connected:
            self.disconnect()

    def connect(self, params: dict) -> dict:
        """
            Connect to ASCOM filterwheel | 连接ASCOM滤镜轮
            Args: 
                host: str # default is "127.0.0.1",
                port: int # default is 11111,
                device_number : int # default is 0
            Returns:
                status : int,
                message : str,
                params : 
                    info : BasicFilterwheelInfo object
        """
        # Check if the filterwheel had already been connected , if true just return the current status
        if self.info._is_connected or self.device is not None:
            log.logw(_("Filterwheel is connected, please do not execute connect command again"))
            return log.return_warning(_("Filterwheel is connected"),{"info":self.info.get_dict()})
        # Check if the parameters are correct
        host = params.get('host')
        port = params.get('port')
        device_number = params.get('device_number')
        # If the host or port is null
        if host is None or port is None or device_number is None:
            log.logw(_("Host and port must be specified"))
            return log.return_warning(_("Host or port or device_number is None"),{})
        # Trying to connect to the specified filterwheel
        try:
            self.device = FilterWheel(host + ":" + str(port), device_number)
            self.device.Connected = True
        except DriverException as e:
            log.loge(_("Faild to connect to device on {}:{} : {}").format(host,port,e))
            return log.return_error(_("Failed to connect to device"),{"error" : e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error while connecting to filterwheel"),{"error" : e})
        log.log(_("Connected to device successfully"))
        res = self.get_configration()
        if res.get('status') != 0:
            return log.return_error(_(f"Failed tp load filterwheel configuration"),{})
        self.info._is_connected = True
        self.info._type = "ascom"
        return log.return_success(_("Connect to filterwheel successfully"),{"info":res.get("info")})

    def disconnect(self) -> dict:
        """
            Disconnect from ASCOM filterwheel | 断链
            Args: None
            Returns: 
                status : int,
                message : str,
                params : None
            NOTE : This function must be called before destory all server
        """
        if not self.info._is_connected or self.device is None:
            log.logw(_("Filterwheel is not connected, please do not execute disconnect command"))
            return log.return_warning(_("Filterwheel is not connected"),{})
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
        log.log(_("Disconnected from filterwheel successfully"))
        return log.return_success(_("Disconnect from filterwheel successfully"),{})

    def reconnect(self) -> dict:
        """
            Reconnect to ASCOM filterwheel | 重连
            Args: None
            Returns: 
                status : int,
                message : str,
                params : dict
                    info : BasicFilterwheelInfo object
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_("Filterwheel is not connected, please do not execute reconnect command"))
            return log.return_warning(_("Filterwheel is not connected"),{}) 
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
        log.log(_("Reconnect filterwheel successfully"))
        self.info._is_connected = True
        return log.return_success(_("Reconnect filterwheel successfully"),{"info" : self.info.get_dict()})

    def scanning(self) -> dict:
        """
            Scan the filterwheel | 扫描电调
            Args: None
            Returns: 
                status : int,
                message : str,
                params : 
                    filterwheel : list
        """

    def polling(self) -> dict:
        """
            Polling for ASCOM filterwheel
            Args: None
            Returns: 
                status : int,
                message : str,
                params : 
                    info : BasicFilterwheelInfo object
        """
        if self.device is None or not self.info._is_connected:
            log.logw(_("Filterwheel is not connected, please do not execute polling command"))
            return log.return_warning(_("Filterwheel is not connected"),{})
        res = self.info.get_dict()
        log.logd(_(f"New filterwheel info : {res}"))
        return log.return_success(_("Filterwheel's information is refreshed"),{"info":res})

    def get_configration(self) -> dict:
        """
            Get filterwheel infomation | 获取滤镜轮信息
            Args: None
            Returns: 
                status : int,
                message : str,
                params : 
                    info : BasicFilterwheelInfo object
        """
        try:
            self.info._name = self.device.Name
            log.logd(_(f"Filterwheel name : {self.info._name}"))
            self.info._id = self.device._client_id
            log.logd(_(f"Filterwheel ID : {self.info._id}"))
            self.info._description = self.device.Description
            log.logd(_(f"Filterwheel description : {self.info._description}"))
            self.info._ipaddress = self.device.address
            log.logd(_(f"Filterwheel IP address : {self.info._ipaddress}"))
            self.info._api_version = self.device.api_version
            log.logd(_(f"Filterwheel API version : {self.info._api_version}"))

            self.info._filter_offset = self.device.FocusOffsets
            log.logd(_("Filterwheel Filter Offset : ").format(self.info._filter_offset))
            self.info._filter_name = self.device.Names
            log.logd(_("Filterwheel Filter Name : ").format(self.info._filter))
            self.info._current_position = self.device.Position
            log.logd(_("Filterwheel Current Position : ").format(self.info._current_position))

        except NotConnectedException as e:
            log.loge(_("Filterwheel is not connected : {}").format(e))
            return log.return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Drvier error : {}").format(e))
            return log.return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error":e})

        log.log(_("Get filterwheel configuration successfully"))
        return log.return_success(_("Get filterwheel configuration successfully"),{"info" : self.info.get_dict()})

    def set_configration(self, params: dict) -> dict:
        return super().set_configration(params)

    def load_configration(self) -> dict:
        return super().load_configration()

    def save_configration(self) -> dict:
        """
            Save configration of filterwheel
            Args : None
            Return : 
                status : int,
                message : str,
                params : None
        """
        _p = path.join
        _path = _p("config",_p("filterwheel",self.info._name+".json"))
        if not path.exists("config"):
            mkdir("config")
        if not path.exists(_p("config","filterwheel")):
            mkdir(_p("config","filterwheel"))
        self.info._configration = _path
        with open(_path,mode="w+",encoding="utf-8") as file:
            file.write(dumps(self.info.get_dict(),indent=4,ensure_ascii=False))
        log.log(_("Save filterwheel information successfully"))
        return log.return_success(_("Save filterwheel information successfully"),{})

    # #################################################################
    #
    # The following functions are used to control the filterwheel (all is non-blocking)
    #
    # #################################################################

    def slew_to(self, params: dict) -> dict:
        """
            Let the filterwheel slew to the specified position
            Args :
                params : dict
                    position : int
            Returns :
                status : int
                message : str
                params : None
        """
        if not self.info._is_connected or self.device is None:
            log.loge(_("Filterwheel is not connected"))
            return log.return_error(_("Filterwheel is not connected"),{})

        position = params.get('position')

        if position is None or not isinstance(position,int):
            log.loge(_("Provided position is not valid"))
            return log.return_error(_("Provided position is not valid"),{})

        if not 0 <= position <= len(self.info._filter_name):
            log.loge(_("Provided position is out of range"))
            return log.return_error(_("Provided position is out of range"),{})

        try:
            self.device.Position = position
            self.info._current_position = position
        except InvalidValueException as e:
            log.loge(_("Provided position is not valid : {}").format(e))
            return log.return_error(_("Provided position is not valid"),{"error" : e})
        except NotConnectedException as e:
            log.loge(_("Filterwheel is not connected : {}").format(e))
            return log.return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Drvier error : {}").format(e))
            return log.return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error":e})

        log.log(_("Filterwheel slewed to {}").format(self.info._current_position))

        return log.return_error(_("Filterwheel slewed to target position successfully"),{})

    def get_filters_list(self) -> dict:
        """
            Get a list of filter name and offset
            Args : None
            Reterns : 
                status : int
                message : str
                params : dict
                    offset : list
                    name : list
        """
        if not self.info._is_connected or self.device is None:
            log.loge(_("Filterwheel is not connected"))
            return log.return_error(_("Filterwheel is not connected"),{})

        try:
            self.info._filter_name = self.device.Names
            self.info._filter_offset = self.device.FocusOffsets
        except NotConnectedException as e:
            log.loge(_("Filterwheel is not connected : {}").format(e))
            return log.return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Drvier error : {}").format(e))
            return log.return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error":e})

    def get_current_position(self) -> dict:
        """
            Get the current position of the filterwheel
            Args : None
            Returns : 
                status : int
                message : str
                params : dict
                    position : int
        """
        if not self.info._is_connected or self.device is None:
            log.loge(_("Filterwheel is not connected"))
            return log.return_error(_("Filterwheel is not connected"),{})

        try:
            self.info._current_position = self.device.Position
        except NotConnectedException as e:
            log.loge(_("Filterwheel is not connected : {}").format(e))
            return log.return_error(_("Remote device is not connected"),{"error":e})
        except DriverException as e:
            log.loge(_("Drvier error : {}").format(e))
            return log.return_error(_("Drvier error"),{"error":e})
        except exceptions.ConnectionError as e:
            log.loge(_("Network error : {}").format(e))
            return log.return_error(_("Network error"),{"error":e})

        log.log(_("Get the filterwheel filter name list : {}").format(self.info._filter_name))
        log.log(_("Get the filterwheel filter offset list : {}").format(self.info._filter_offset))

        return log.return_success(_("Get the filterwheel current position successfully"),{
            "offset" : self.info._filter_offset,
            "name" : self.info._filter_name
        })