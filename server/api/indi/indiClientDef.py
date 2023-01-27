# coding=utf-8

"""

Copyright(c) 2023 Gao Le

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

"""
defines the pyindi client for usage
"""

import PyIndi
from .misc import INDI_DEBUG,INDI_LOG_DATA
from .basic_indi_state_str import strIPState, strISState
from ...logging import logger

class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
        self.logger = logger
        self.logger.info('creating an instance of IndiClient')

    def newDevice(self, d):
        self.logger.info("new device " + d.getDeviceName())

    def newProperty(self, p):
        if INDI_DEBUG:
            self.logger.info("new property " + p.getName() + " for device " + p.getDeviceName())

    def removeProperty(self, p):
        if INDI_DEBUG:
            self.logger.info("remove property " + p.getName() + " for device " + p.getDeviceName())

    def newBLOB(self, bp):
        global blob_event1, blob_event2
        print("new BLOB ", bp.name)
        if bp.name == 'CCD1':
            blob_event1.set()
        else:
            blob_event2.set()

    def newSwitch(self, svp):
        if INDI_LOG_DATA:
            this_str = f"new Switch {svp.name}  for device {svp.device} \n"
            for t in svp:
                this_str += "       " + t.name + "(" + t.label + ")= " + strISState(t.s) + '\n'
            self.logger.info(this_str)

    def newNumber(self, nvp):
        if INDI_LOG_DATA:
            this_str = f"new Number {nvp.name} for device {nvp.device} \n"
            for t in nvp:
                this_str += "       " + t.name + "(" + t.label + ")= " + str(t.value) + '\n'
            self.logger.info(this_str)

    def newText(self, tvp):
        if INDI_DEBUG:
            self.logger.info("new Text " + tvp.name + " for device " + tvp.device)

    def newLight(self, lvp):
        if INDI_DEBUG:
            self.logger.info("new Light " + lvp.name + " for device " + lvp.device)

    def newMessage(self, d, m):
        if INDI_DEBUG:
            self.logger.info("new Message " + d.messageQueue(m))

    def serverConnected(self):
        self.logger.info("Server connected (" + self.getHost() + ":" + str(self.getPort()) + ")")

    def serverDisconnected(self, code):
        self.logger.info("Server disconnected (exit code = " + str(code) + "," + str(self.getHost()) + ":" + str(
            self.getPort()) + ")")

