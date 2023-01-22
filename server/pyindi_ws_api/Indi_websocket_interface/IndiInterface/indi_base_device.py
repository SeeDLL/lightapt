"""

"""
from PyIndi import BaseDevice
import PyIndi
from .indiClientDef import IndiClient


class IndiBaseDevice:
    def __init__(self, indi_client: IndiClient, indi_device: BaseDevice = None):
        self.this_device = indi_device
        self.indi_client = indi_client
        if self.this_device is not None:
            self.this_connection_switch = self.this_device.getSwitch("CONNECTION")
        else:
            self.this_connection_switch = None

    def setup_device(self, indi_device: BaseDevice):
        if indi_device is None:
            pass  # show log
        else:
            self.this_device = indi_device
            self.this_connection_switch = self.this_device.getSwitch("CONNECTION")

    def connect(self, indiclient):
        if self.this_device is None:
            pass
        elif not (self.this_device.isConnected()):
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            self.this_connection_switch[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            self.this_connection_switch[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            indiclient.sendNewSwitch(self.this_connection_switch)  # send this new value to the device

    def disconnect(self, indiclient):
        if self.this_device is None:
            pass
        elif self.this_device.isConnected():
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            self.this_connection_switch[0].s = PyIndi.ISS_OFF  # the "CONNECT" switch
            self.this_connection_switch[1].s = PyIndi.ISS_ON  # the "DISCONNECT" switch
            indiclient.sendNewSwitch(self.this_connection_switch)  # send this new value to the device