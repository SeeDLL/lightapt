import time
from .indi_base_device import IndiBaseDevice
from PyIndi import BaseDevice
import tornado.ioloop
from .indiClientDef import IndiClient
from .indi_switch_operation import turn_on_second_swtich, turn_on_first_swtich, turn_on_multiple_switch_by_index
from .indi_property_2_json import indi_property_2_json
import asyncio
import PyIndi
from .misc import indi_logger, blob_event2, blob_event1
import datetime
from pathlib import Path
import json


GAIN_Keywords = ["CCD_GAIN", "ControlN"]


class IndiCameraDevice(IndiBaseDevice):
    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None):
        super().__init__(indi_client, indi_device)
        # telescope basic parameters here, if necessary
        self.can_cool = False
        self.has_fan = False
        self.has_heater = False
        self.has_binning = False
        self.gain_type = 0

        self.fits_save_path = Path.home() / 'Pictures'
        self.subframe_counting = 0
        self.save_file_name_pattern = '{date}/{target_name}_{filter}_{exposure}_{date_time}_{HFR}_{guiding_RMS}_{count}.fits'

        self.indi_client.setBLOBMode(PyIndi.B_ALSO, self.this_device.getDeviceName(), "CCD1")
        # important flag
        self.in_exposure = False  # flag for camera is working

    def check_camera_params(self):
        """
        called directly after connection.
        :return:
        """
        # check cool
        time.sleep(1)
        t_s = self.this_device.getSwitch('CCD_COOLER')
        if (t_s):
            self.can_cool = True
        else:
            self.can_cool = False

        # check fan
        t_s = self.this_device.getSwitch('TC_FAN_CONTROL')
        if (t_s):
            self.has_fan = True
        else:
            self.has_fan = False

        # check heat
        t_s = self.this_device.getSwitch('TC_HEAT_CONTROL')
        if (t_s):
            self.has_heater = True
        else:
            self.has_heater = False
        # check gain keyword type 
        for (index, one_keyword) in enumerate(GAIN_Keywords):
            t_s = self.this_device.getNumber(one_keyword)
            if (t_s):
                self.gain_type = index
        # check binning
        t_s = self.this_device.getNumber("CCD_BINNING")
        if (t_s):
            self.has_binning = True
        else:
            self.has_binning = False

    async def set_cool_target_temperature(self, target_temperature: float, **kwargs):
        temperature = self.this_device.getNumber("CCD_TEMPERATURE")
        temperature[0].value = target_temperature
        self.indi_client.sendNewNumber(temperature)
        return None

    async def get_static_info(self, **kwargs):
        # pixel size, 
        ccd_info = self.this_device.getNumber("CCD_INFO")
        return indi_property_2_json(ccd_info)  # todo to json

    async def get_set_params(self, **kwargs):
        # gain offset, binning
        ret_json = {}
        gain = self.this_device.getNumber(GAIN_Keywords[self.gain_type])
        ret_json['gain'] = gain[0].value
        offset = self.this_device.getNumber("CCD_OFFSET")
        ret_json['offset'] = offset[0].value
        if self.has_binning:
            binning = self.this_device.getNumber("CCD_BINNING")
            ret_json['binning'] = binning[0].value
        else:
            ret_json['binning'] = None
        return ret_json

    async def get_real_time_info(self, **kwargs):
        temperature = self.this_device.getNumber("CCD_TEMPERATURE")
        return {
            "temperature": temperature[0].value,
            "in_exposure": self.in_exposure,
        }

    async def start_cool_camera(self, **kwargs):
        """
           > CCD_COOLER type switch
               COOLER_ON(ON)= On
               COOLER_OFF(OFF)= Off
        :return:
        """
        if self.can_cool:
            ccd_cooler = self.this_device.getSwitch('CCD_COOLER')
            ccd_cooler = turn_on_first_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
            return None
        else:
            return 'No Cooler Available!'

    async def stop_cool_camera(self, **kwargs):
        if self.can_cool:
            ccd_cooler = self.this_device.getSwitch('CCD_COOLER')
            ccd_cooler = turn_on_second_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
            return None
        else:
            return 'No Cooler Available!'

    async def start_fan(self, **kwargs):
        """
           > TC_FAN_CONTROL type switch
               TC_FAN_ON(On)= On
               TC_FAN_OFF(Off)= Off
        :return:
        """
        if self.has_fan:
            ccd_cooler = self.this_device.getSwitch('TC_FAN_CONTROL')
            ccd_cooler = turn_on_first_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Fan Available'

    async def stop_fan(self, **kwargs):
        if self.has_fan:
            ccd_cooler = self.this_device.getSwitch('TC_FAN_CONTROL')
            ccd_cooler = turn_on_second_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Fan Available'

    async def start_tc_heat(self, **kwargs):
        """
           > TC_HEAT_CONTROL type switch
               TC_HEAT_OFF(Off)= On
               TC_HEAT_ON(On)= Off
        :return:
        """
        if self.has_heater:
            ccd_cooler = self.this_device.getSwitch('TC_FAN_CONTROL')
            ccd_cooler = turn_on_first_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Heater Available'

    async def stop_tc_heat(self, **kwargs):
        if self.has_heater:
            ccd_cooler = self.this_device.getSwitch('TC_FAN_CONTROL')
            ccd_cooler = turn_on_second_swtich(ccd_cooler)
            self.indi_client.sendNewSwitch(ccd_cooler)
        else:
            return 'No Heater Available'

    """
    kwargs define for file name formatting.
    target_info: obj, the name of target. countain name, coord
    filter_info: object, the filter basic information given by the indi_filter_wheel
    phd2_object: TBD, how to get the realtime guiding rmse.   
    
    keywords for generating format
    target_name:        str, target name
    count:              int, default by 0, sequence subframe number.
    other automatically generated parameters
    exposure    given directly by parameter
    HFR         calculated by ??? TBD
    guiding_rms phd2 guiding accuracy
    date        the date when this fits file is generated.
    date_time   the date time when this fits file is generated. format %Y-%m-%d-%H-%M
    
    note: if the file name is already exists, extra _1 will be added.
    
    '{date}/{target_name}_{filter}_{exposure}_{date_time}_{HFR}_{guiding_RMS}_{count}.fits'
    """
    def __translate_parameters_formatting(self, **kwargs):
        if 'target_info' in kwargs.keys():
            target_name = kwargs['target_info']['name']
        else:
            target_name = ''
        if 'count' in kwargs.keys():
            count = kwargs['count']
        else:
            count = self.subframe_counting
            self.subframe_counting += 1
        if 'filter_info' in kwargs.keys():
            filter = None
        else:
            filter = 'none'
        if 'phd2_object' in kwargs.keys():
            guiding_RMS = None
        else:
            guiding_RMS = ''
        now = datetime.datetime.now()
        now_str = now.strftime('%Y-%m-%d-%H-%M-%S')
        date_str = now.strftime('%Y-%m-%d')
        file_name = self.save_file_name_pattern.format(
            target_name=target_name, count=count, filter=filter, guiding_RMS=guiding_RMS, HFR=kwargs['HFR'],
            date=date_str, date_time=now_str, exposure=kwargs['exposure_time']
        )
        file_path = self.fits_save_path / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            new_file_path = file_path.parent / file_name.replace('.fits', '_1.fits')
            file_path = new_file_path
        return file_path

    async def start_single_exposure(self, exposure_time: float, *args, **kwargs):
        """

        :param exposure_time: must have
        :param args:  args[0] is subframe count, if no subframe count is given, system will use self_increase count
        :param kwargs:
        :return:
        """
        if self.in_exposure:
            return 'Exposure is in progress. Cannot start exposure now!'

        ccd_exposure = self.this_device.getNumber("CCD_EXPOSURE")
        ccd_exposure[0].value = exposure_time
        blob_event1.clear()
        self.indi_client.sendNewNumber(ccd_exposure)
        self.in_exposure = True
        indi_logger.info(f'device camera, start exposure {exposure_time} seconds')
        ccd_ccd1 = self.this_device.getBLOB('CCD1')

        if len(args) >= 1:
            kwargs['count'] = args[0]
        kwargs['exposure_time'] = exposure_time
        kwargs['ccd1'] = ccd_ccd1
        tornado.ioloop.IOLoop.instance().add_callback(self.after_exposure_finish, *args, **kwargs)

    async def after_exposure_finish(self, *args, **kwargs):
        try:
            await asyncio.wait_for(blob_event1.wait(), timeout=kwargs['exposure_time']+2)
            self.in_exposure = False
            indi_logger.info(f'device camera, ended exposure {kwargs["exposure_time"]} seconds')
            for blob in kwargs['ccd1']:
                fits = blob.getblobdata()
                kwargs['HFR'] = 0  # to detect HFR value
                to_save_file_path = self.__translate_parameters_formatting(**kwargs)
                with open(str(to_save_file_path), 'wb') as f:
                    f.write(fits)
            kwargs['ws_instance'].write_message(json.dumps({
                'type': 'signal',
                'message': 'Exposure Finished!',
                'data': None,
            }))
        except TimeoutError:
            blob_event1.clear()
            self.in_exposure = False
            kwargs['ws_instance'].write_message(json.dumps({
                'type': 'signal',
                'message': 'ERROR! Exposure Time Out Error!',
                'data': None,
            }))

    async def abort_exposure(self, **kwargs):
        if not self.in_exposure:
            return 'No exposure in progress!'
        else:
            abort_exposure = self.this_device.getSwitch('CCD_ABORT_EXPOSURE')
            abort_exposure = turn_on_multiple_switch_by_index(abort_exposure, 0)
            self.indi_client.sendNewSwitch(abort_exposure)
            self.in_exposure = False
            return 'Exposure aborted!'

    async def set_parameters(self, **kwargs):
        pass

    async def get_parameter(self, **kwargs):
        pass
