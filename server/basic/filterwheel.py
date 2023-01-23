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

from server.basic.device import BasicDeviceAPI

class BasicFilterwheelInfo(object):
    """
        Basic filterwheel info container
    """
    _type = "" # type of the camera , must be given
    _name : str # name of the camera
    _id : int # id of the camera
    _description : str
    _timeout = 5
    _configration = "" # path to the configuration file

    _ipaddress : str # IP address only ASCOM and INDI
    _api_version : str # API version only ASCOM and INDI

    _filter_offset : list # list of filter offset
    _filter_name : list # list of filter name

    _current_position : int # current position

    _is_connected : bool # Is the filterwheel connected
    _is_slewing : bool # Is the filterwheel moving

class BasicFilterwheelAPI(BasicDeviceAPI):
    """
        Basic filterwheel API
    """

    def __init__(self) -> None:
        super().__init__()

    def __del__(self) -> None:
        return super().__del__()

    # #################################################################
    #
    # Filterwheel Basic API
    #
    # #################################################################

    def slew_to(self,params : dict) -> dict:
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

    def get_current_position(self) -> dict:
        """
            Get the current position of the filterwheel
            Args : None
            Reterns :
                status : int
                message : str
                params : dict
                    position : int
        """