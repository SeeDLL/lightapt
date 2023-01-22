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

from flask import Flask, render_template
from PIL import Image, ImageDraw
import time, base64, math, io, sys

import server.plugins.gps3 as gps3

from server.webapp import socketio
from utils.i18n import _
from utils.lightlog import lightlog
logger = lightlog(__name__)

# define colors for skymap
white = (255, 255, 255)
ltgray = (191, 191, 191)
mdgray = (127, 127, 127)
dkgray = (63, 63, 63)
black = (0, 0, 0)
red = (255, 0, 0)
brightgreen = (0, 255, 0)
darkgreen = (0, 192, 0)
blue = (0, 0, 255)
cyan = (0, 255, 255)
magenta = (255, 0, 255)
yellow = (255, 255, 0)
orange = (255, 128, 0)

class WebGPS(object):
    """
        Web GPS interface
    """

    def __init__(self) -> None:
        """
            Initialize the Web GPS interface
        """
        try:
            self.gpsd_socket = gps3.GPSDSocket()
            self.gpsd_socket.connect()
            self.gpsd_socket.watch()
            self.data_stream = gps3.DataStream()
        except:
            logger.loge(_("Failed to start GPS connection , please try again or install gpsd as the server"))
        self.thread = None

    def __del__(self) -> None:
        """
            Delete the gpsd socket
        """
        self.gpsd_socket.close()

    def background_thread(self):
        for new_data in self.gpsd_socket:
            if new_data:
                self.data_stream.unpack(new_data)
                if isinstance(self.data_stream.TPV['mode'], int):
                    socketio.emit('gpspanel', {
                        'mode': self.data_stream.TPV['mode'],
                        'latitude': self.data_stream.TPV['lat'],
                        'longitude': self.data_stream.TPV['lon'],
                        'gpstime': self.data_stream.TPV['time'],
                        'altitude': self.data_stream.TPV['alt']
                    })
                if isinstance(self.data_stream.SKY['satellites'], list):
                    socketio.emit('gpspanel',{
                        'hdop': self.data_stream.SKY['hdop'],
                        'vdop': self.data_stream.SKY['vdop'],
                        'sschart': self.signal_strength(self.data_stream.SKY['satellites']),
                        'satellites': self.data_stream.SKY['satellites'],
                        'skymap': self.skymap(self.data_stream.SKY['satellites'])
                    })
            else:
                time.sleep(0.1)

    def signal_strength(self,satellites) -> str:
        # set image size
        imgsize = 450, 100

        # create empty image
        img = Image.new('RGBA', imgsize, (255,255,255,32))
        draw = ImageDraw.Draw(img)

        x = -3

        for s in satellites:
            # set colors
            if s['ss'] >= 40:
                color = (153, 204, 0)
            if s['ss'] >= 30:
                color = (255, 153, 0)
            if s['ss'] < 30:
                color = (204, 0, 0)
            if s['ss'] < 10:
                color = (102, 102, 102)

            # draw bars
            x = x + 35
            y = 100 - int(s['ss'])
            draw.line((x,100,x,y), width=25, fill=color)

            # draw labels
            draw.text((x - 12, 90), '{:3d}'.format(s['PRN']), fill=white)

        # draw title
        draw.text((x / 2, 10), 'Signal Strength', fill=white)

        # encode and return
        imgdata = io.BytesIO()
        img.save(imgdata, format="PNG")
        imgdata_encoded = base64.b64encode(imgdata.getvalue()).decode()
        return imgdata_encoded

    def skymap(self,satellites) -> str:
        # set image size
        sz = 400

        # create empty image
        img = Image.new('RGBA', (sz, sz), (255,255,255,0))
        draw = ImageDraw.Draw(img)

        # draw arcs
        draw.chord([(sz * 0.02, sz * 0.02), (sz * 0.98, sz * 0.98)], 0, 360, fill = mdgray, outline = black)
        draw.text((sz/2 * 0.98 - 5, sz * 0.02), "0", fill = ltgray)
        draw.chord([(sz * 0.05, sz * 0.05), (sz * 0.95, sz * 0.95)], 0, 360, fill = dkgray, outline = ltgray)
        draw.text((sz/2 * 0.98 - 5, sz * 0.05), "5", fill = ltgray)

        # azimuth lines
        for num in range(0, 180, 15):
            #turn into radians
            angle = math.radians(num)

            # determine length of radius
            r = sz * 0.95 * 0.5

            # and convert length/azimuth to cartesian
            x0 = int((sz * 0.5) - (r * math.cos(angle)))
            y0 = int((sz * 0.5) - (r * math.sin(angle)))
            x1 = int((sz * 0.5) + (r * math.cos(angle)))
            y1 = int((sz * 0.5) + (r * math.sin(angle)))
            draw.line([(x0, y0), (x1, y1)], fill = ltgray)

        # draw labels
        draw.text((sz * 0.98 / 2 + 8, sz * 0.02 + 1), "N", fill = white)
        draw.text((sz * 0.98 / 2 - 5, sz * 0.98 - 12), "S", fill = white)
        draw.text((sz * 0.98 - 8, sz * 0.98 / 2 + 5), "W", fill = white)
        draw.text((sz * 0.02 + 5, sz * 0.98 / 2 - 8), "E", fill = white)


        # elevation lines
        for num in range (15, 90, 15):
            x0 = sz * 0.5 - num * 2
            y0 = sz * 0.5 - num * 2
            x1 = sz * 0.5 + num * 2
            y1 = sz * 0.5 + num * 2

            # draw labels
            draw.arc([(x0, y0), (x1, y1)], 0, 360, fill = ltgray)
            draw.text((sz/2 * 0.98 - 10, sz * 0.5 - num * 2), '{:d}'.format(90 - num), fill = ltgray)

        # satellites
        for s in satellites:
            if (s['PRN'] != 0) and (s['el'] + s['az'] + s['ss'] != 0) and (s['el'] >= 0 and s['az'] >= 0):
                if s['ss'] >= 40:
                    color = (153, 204, 0)
                if s['ss'] >= 30:
                    color = (255, 153, 0)
                if s['ss'] < 30:
                    color = (204, 0, 0)
                if s['ss'] < 10:
                    color = (102, 102, 102)

                # circle size
                ssz = 16

                #rotate coords -> 90deg W = 180deg trig
                az = s['az'] + 90
                az = math.radians(az)

                # determine length of radius
                r = sz * 0.98 * 0.5 - ssz
                r -= int(r * s['el'] / 90)

                # convert length/azimuth to cartesian
                x = int((sz * 0.5) - (r * math.cos(az)))
                y = int((sz * 0.5) - (r * math.sin(az)))

                # swap coords
                x = sz * 0.98 - x;

                # draw satellites
                if s['used'] == True:
                    draw.chord([(x, y), (x + ssz, y + ssz)], 0, 360, fill = color)
                else:
                    draw.arc([(x, y), (x + ssz, y + ssz)], 0, 360, fill = color)

                # draw labels
                draw.text((x + ssz/5, y + ssz/5), '{:2d}'.format(s['PRN']), fill = white)

        # draw legend
        draw.rectangle([(sz - 26, sz - 90), (sz - 1, sz - 10)], fill = (153, 204, 0), outline = black)
        draw.rectangle([(sz - 26, sz - 70), (sz - 1, sz - 10)], fill = (255, 153, 0), outline = black)
        draw.rectangle([(sz - 26, sz - 50), (sz - 1, sz - 10)], fill = (204, 0, 0), outline = black)
        draw.rectangle([(sz - 26, sz - 30), (sz - 1, sz - 10)], fill = (102, 102, 102), outline = black)
        draw.text((sz - 21, sz - 85), "40+", fill = black)
        draw.text((sz - 21, sz - 65), "30+", fill = black)
        draw.text((sz - 21, sz - 45), "-30", fill = black)
        draw.text((sz - 21, sz - 25), "-10", fill = black)

        # encode and return
        imgdata = io.BytesIO()
        img.save(imgdata, format="PNG")
        imgdata_encoded = base64.b64encode(imgdata.getvalue()).decode()
        return imgdata_encoded


