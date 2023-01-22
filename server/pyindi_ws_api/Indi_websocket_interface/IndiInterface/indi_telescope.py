import time
from .indi_base_device import IndiBaseDevice
from PyIndi import BaseDevice
from .indiClientDef import IndiClient
import PyIndi
from .basic_indi_state_str import *
from .indi_switch_operation import turn_on_multiple_switch_by_index
from .indi_property_2_json import indi_keyword_2_json

home_keyword = ["AT_HOME", "HomeS"]


class IndiTelescopeDevice(IndiBaseDevice):
    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None):
        super().__init__(indi_client, indi_device)
        # telescope basic parameters here, if necessary
        
        self.longitude = None
        self.latitude = None
        self.elevation = None
        self.ha_limit = None  # todo, not available yet.
        self.telescope_aperture = None
        self.telescope_focal_length = None
        self.guider_aperture = None
        self.guider_focal_length = None
        
        # initial after connection
        self.can_park = False
        self.can_home = False
        self.home_word_type = None
        self.can_track_speed = False
        self.can_slew_speed = False
        self.can_guide_speed = False

        # target_information related
        self.target_name = None
        self.target_coord = None
    
    def check_telescope_params(self):
        # check park
        t_s = self.this_device.getSwitch('TELESCOPE_PARK')
        if (t_s):
            self.can_park = True
        else:
            self.can_park = False
        # check home
        self.can_home = False
        for (index, one_keyword) in enumerate(home_keyword):
            t_s = self.this_device.getSwitch(one_keyword)
            if (t_s):
                self.can_home = True
                self.home_word_type = index
        # check track
        t_s = self.this_device.getSwitch('TELESCOPE_TRACK_MODE')
        if (t_s):
            self.can_track_speed=True
        else:
            self.can_track_speed=False
        # check slew
        t_s = self.this_device.getSwitch('SlewRateS')
        if (t_s):
            self.can_slew_speed=True
        else:
            self.can_slew_speed=False
        # check guide speed
        t_s = self.this_device.getSwitch('GuideRateN')
        if (t_s):
            self.can_guide_speed=True
        else:
            self.can_guide_speed=False
    
    async def set_long_lat(self, long: float, lat: float, elev=0):
        if long > 180 or long < -180:
            raise ValueError('longitude not in range!')
        if lat > 90 or long < -90:
            raise ValueError('latitude not in range!')
        self.longitude = long
        self.latitude = lat
        self.elevation = elev
        geo_coord = self.this_device.getNumber('GEOGRAPHIC_COORD')
        geo_coord[0].value = lat  # latitude
        geo_coord[1].value = long  # longitude
        geo_coord[2].value = float(elev)  # elevation
        self.indi_client.sendNewNumber(geo_coord)
        return None

    async def get_static_info(self):
        pass
    
    async def get_set_params(self):
        return indi_keyword_2_json(self.this_device, "MOUNT_TYPE", "ON_COORD_SET", "TELESCOPE_TRACK_MODE",
                                   "TELESCOPE_TRACK_STATE", "GEOGRAPHIC_COORD")

    async def get_real_time_info(self):
        # return ra, dec, in_moving,
        equad_eod_coord = self.this_device.getNumber("EQUATORIAL_EOD_COORD")
        ra = equad_eod_coord[0].value
        dec = equad_eod_coord[1].value
        state_d = equad_eod_coord.getState()
        state = strIPState(state_d)
        if state_d == PyIndi.IPS_BUSY:
            is_moving = True
        else:
            is_moving = False
        return {
            'ra': ra,
            'dec': dec,
            'state': state,
            'is_moving': is_moving
        }

    async def set_telescope_info(self, telescope_aperture: float, telescope_focal_length: float,
                                 guider_aperture: float, guider_focal_length: float):
        self.telescope_aperture = telescope_aperture
        self.telescope_focal_length = telescope_focal_length
        self.guider_aperture = guider_aperture
        self.guider_focal_length = guider_focal_length
        telescope_info = self.this_device.getNumber('TELESCOPE_INFO')
        t_a = telescope_info.findWidgetByName('TELESCOPE_APERTURE')
        t_a.value = telescope_aperture
        t_f = telescope_info.findWidgetByName('TELESCOPE_FOCAL_LENGTH')
        t_f.value = telescope_focal_length
        g_a = telescope_info.findWidgetByName('GUIDER_APERTURE')
        g_a.value = guider_aperture
        g_f = telescope_info.findWidgetByName('GUIDER_FOCAL_LENGTH')
        g_f.value = guider_focal_length
        self.indi_client.sendNewNumber(telescope_info)
        return None

    async def set_time(self):
        """
        note indi will sync time directly it connected to telescope device.
        so if the machine time is correct, then there is no need to change time.
        :return:
        """
        pass

    async def set_track(self):
        on_coord_set = self.this_device.getSwitch("ON_COORD_SET")
        on_coord_set[0].s = PyIndi.ISS_ON  # TRACK
        on_coord_set[1].s = PyIndi.ISS_OFF  # SLEW
        on_coord_set[2].s = PyIndi.ISS_OFF  # SYNC
        self.indi_client.sendNewSwitch(on_coord_set)
        return None

    async def start_track(self):
        track_state = self.this_device.getSwitch('TELESCOPE_TRACK_STATE')
        track_state[0].s = PyIndi.ISS_ON
        track_state[1].s = PyIndi.ISS_OFF
        self.indi_client.sendNewSwitch(track_state)
        return None

    async def set_track_mode(self, track_mode):
        """

        :param track_mode: sidereal, solar, lunar
        :return:
        """
        track_mode = self.this_device.getSwitch("TELESCOPE_TRACK_MODE")
        if track_mode == 'sidereal':
            track_mode = turn_on_multiple_switch_by_index(track_mode, 0)
        elif track_mode == 'solar':
            track_mode = turn_on_multiple_switch_by_index(track_mode, 1)
        elif track_mode == 'lunar':
            track_mode = turn_on_multiple_switch_by_index(track_mode, 2)
        else:
            raise TypeError('wrong tracking name!')
        self.indi_client.sendNewSwitch(track_mode)
        return None

    async def stop_track(self):
        track_state = self.this_device.getSwitch('TELESCOPE_TRACK_STATE')
        track_state[0].s = PyIndi.ISS_OFF
        track_state[1].s = PyIndi.ISS_ON
        self.indi_client.sendNewSwitch(track_state)
        return None

    async def goto(self, ra: float, dec: float, target_name=None, *args, **kwargs):
        if self.__is_parked():
            return 'telescope is parked, please unpark first!'
        equad_eod_coord = self.this_device.getNumber("EQUATORIAL_EOD_COORD")
        if equad_eod_coord.getState() == PyIndi.IPS_BUSY:
            return 'telescope is moving, please wait!'
        equad_eod_coord[0].value = ra
        equad_eod_coord[1].value = dec
        self.indi_client.sendNewNumber(equad_eod_coord)
        if target_name is not None:
            self.target_name = target_name
            self.target_coord = {
                'ra': ra,
                'dec': dec
            }
        else:
            self.target_name = None
            self.target_coord = None
        return None

    async def goto_ha_dec(self, ha: float, dec: float,  target_name=None):
        pass

    async def got_az_al(self, az: float, al: float,  target_name=None):
        pass

    async def get_fits_file_format_data(self):
        if self.target_name is not None:
            return {
                'name': self.target_name,
                'coord': self.target_coord
            }
        else:
            return None

    async def home(self):
        """
        default as goto ha=-6, dec=90
        found, if the telescope support home instruction, it will have return_home, at_home property.
        :return:
        """
        pass

    def __is_parked(self):
        park = self.this_device.getSwitch('TELESCOPE_PARK')
        if park[0] == PyIndi.ISS_ON:
            return True
        else:
            return False

    async def park(self):
        if self.can_park:
            park = self.this_device.getSwitch('TELESCOPE_PARK')
            park[0] = PyIndi.ISS_ON
            park[1] = PyIndi.ISS_OFF
            self.indi_client.sendNewSwitch(park)
            return None
        else:
            return 'Telescope cannot park'

    async def unpark(self):
        if self.can_park:
            park = self.this_device.getSwitch('TELESCOPE_PARK')
            park[0] = PyIndi.ISS_OFF
            park[1] = PyIndi.ISS_ON
            self.indi_client.sendNewSwitch(park)
            return None
        else:
            return 'Telescope cannot park'            

    async def set_park(self, ha, dec):
        pass

    async def abort(self):
        abort = self.this_device.getSwitch('TELESCOPE_ABORT_MOTION')
        abort[0] = PyIndi.ISS_ON
        self.indi_client.sendNewSwitch(abort)
        return None
