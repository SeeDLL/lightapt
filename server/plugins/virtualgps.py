# coding=utf-8

"""

Copyright(c) 2022-2023 Max Qian  <astroair.cn>

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

# #########################################################################
#
# This file is modified from https://github.com/rkaczorek/virtualgps
#
# #########################################################################

import os,time, datetime, re,platform

__author__ = 'Radek Kaczorek'
__modified_by__ = 'Max Qian'
__copyright__ = 'Copyright 2019  Radek Kaczorek | Copyright 2023 Max Qian'
__license__ = 'GPL-3'
__version__ = '1.1.1'

if __name__ == '__main__':
    os.chdir("".join(os.getcwd()))

from utils.lightlog import lightlog
logger = lightlog(__name__)
import server.config as c
from utils.i18n import _

class VirtualGPS(object):
    """
        Create a virtual GPS object for other softwares like Kstars to connect to
        
        # NMEA minimal sequence:
        #$GPGGA,231531.521,5213.788,N,02100.712,E,1,12,1.0,0.0,M,0.0,M,,*6A
        #$GPGSA,A,1,,,,,,,,,,,,,1.0,1.0,1.0*30
        #$GPRMC,231531.521,A,5213.788,N,02100.712,E,,,261119,000.0,W*72
    """

    def __init__(self) -> None:
        """
            Initialize the virtual GPS object
            Args : None
            Returns : None
        """

        self.virtualgps_dev = "/tmp/vgps"
        self.master = None
        self.slave = None
        self.pty = None
        self.can_run = True

    def __del__(self) -> None:
        """
            Delete the virtual GPS object
            Args : None
            Returns : None
        """
        try:
            os.remove(self.virtualgps_dev)
        except OSError as e:
            logger.loge(_("Failed to remove virtualgps file : {}").format(e))
        os.close(self.master)
        os.close(self.slave)

    def convert_to_sexagesimal(self,coord):
        """
        Convert a string of coordinates using delimiters for minutes ('),
        seconds (") and degrees (º). It also supports colon (:).
            >>> from virtualgps import convert_to_sexagesimal
            >>> convert_to_sexagesimal(u"52:08.25:1.5\"")
            52.13791666666667
            >>> convert_to_sexagesimal(u"52:08:16.5\"")
            52.13791666666667
            >>> convert_to_sexagesimal(u"52.1:02:16.5\"")
            52.13791666666667
            >>> convert_to_sexagesimal(u"52º08'16.5\"")
            52.13791666666667
        :param coord: Coordinates in string representation
        :return: Coordinates in float representation
        """
        elements = re.split(r'[\u00ba\':\"]', coord)

        degrees = float(elements[0])
        if (len(elements) - 1) > 0:
            # Convert minutes to degrees
            degrees += float(elements[1]) / 60
        if (len(elements) - 1) > 1:
            # Convert seconds to degrees
            degrees += float(elements[2]) / 3600
        return degrees


    def nmea_checksum(self,sentence):
        chsum = 0
        for s in sentence:
            chsum ^= ord(s)
        return hex(chsum)[2:]

    def start(self) -> None:
        """
            Start a new virtual gps
            Args : None
            Returns : None
        """
        if platform.system() == "Windows":
            logger.logw(_("Windows is not supported to start a virtual GPS"))
            logger.logw(_("This is because Windows do not support virtual tty devices"))
        else:
            # create pseudo terminal device
            self.master, self.slave = os.openpty()
            self.pty = os.ttyname(self.slave)

            # remove leftovers before setting virtual dev
            if os.path.isfile(self.virtualgps_dev):
                os.remove(self.virtualgps_dev)

            if not os.path.islink(self.virtualgps_dev):
                os.symlink(self.pty,self.virtualgps_dev)

            # load location data from config
            if 'lat' in c.config['virtualgps'] and 'lon' in c.config['virtualgps'] and 'elevation' in c.config['virtualgps']:
                latitude = self.convert_to_sexagesimal(c.config['virtualgps']['lat'])
                longitude = self.convert_to_sexagesimal(c.config['virtualgps']['lon'])
                elevation = float(c.config['virtualgps']['elevation'])
                logger.logd(_("Virtual GPS Location : latitude {} and longitude {}").format(latitude,longitude))
            else:
                logger.loge(_("No virtual GPS location found"))
                return

            # W or E
            if latitude > 0:
                NS = 'N'
            else:
                NS = 'S'

            # N or S
            if longitude > 0:
                WE = 'E'
            else:
                WE = 'W'

            # format for NMEA
            latitude = abs(latitude)
            longitude = abs(longitude)
            lat_deg = int(latitude)
            lon_deg = int(longitude)
            lat_min = (latitude - lat_deg) * 60
            lon_min = (longitude - lon_deg) * 60
            latitude = "%02d%07.4f" % (lat_deg, lat_min)
            longitude = "%03d%07.4f" % (lon_deg, lon_min)
            while True:
                if self.can_run:
                    now = datetime.datetime.utcnow()
                    date_now = now.strftime("%d%m%y")
                    time_now = now.strftime("%H%M%S")

                    # assemble nmea sentences
                    gpgga = "GPGGA,%s,%s,%s,%s,%s,1,12,1.0,%s,M,0.0,M,," % (time_now, latitude, NS, longitude, WE, elevation)
                    gpgsa = "GPGSA,A,3,,,,,,,,,,,,,1.0,1.0,1.0"
                    gprmc = "GPRMC,%s,A,%s,%s,%s,%s,,,%s,000.0,W" % (time_now, latitude, NS, longitude, WE, date_now)

                    # add nmea checksums
                    gpgga = "$%s*%s\n" % (gpgga, self.nmea_checksum(gpgga))
                    gpgsa = "$%s*%s\n" % (gpgsa, self.nmea_checksum(gpgsa))
                    gprmc = "$%s*%s\n" % (gprmc, self.nmea_checksum(gprmc))

                    os.write(self.master, gpgga.encode())
                    os.write(self.master, gpgsa.encode())
                    os.write(self.master, gprmc.encode())

                    time.sleep(1)

        