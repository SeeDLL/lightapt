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

# #################################################################
#
# NOTE : Solver is not like other devices , it does not need to connect or get information,
#        we just need to call the command to solve the image we saved , and return the result
#        to the client.
#        To improve the performance , we need to get the correct coordinates in the image and 
#        the view of the camera , other general commands will be added automatically.
#        What's more , both astrometry and astap can be used to solve , and we can use them in
#        one time , no need to care about the compatibility or other strange things.
#
# #################################################################

from utils.i18n import _
from ..logging import logger

class WSSolver(object):
    """
        Websocket solver interface

        Astrometry API
        As we know that there are two API to use astrometry as the solver.

        One is online api that we need to send the image to the server,
        and get the results from the server.Because of the poor network
        condition and apikey required. So online api is not available.

        Other one is via the command line to control the solver , this is
        very convenient but will cost a lot of memory and cpu usage.If we run
        in a old machine , it may cost up to a few minutes to complete
        and will make we mad.So if we do this on a new machine , nothing bad
        is going to happen.By our testing , the fast time is 3 seconds per image

        We will both support two api , and you can choose the fit one to use.

        Astap API
        Astap is a new solver and the speed is very fast. And the community supports
        is very good, so this is a good choice too.
    """

    def __init__(self,ws) -> None:
        """
            Initialize the solver (what to initialize)
            Args : None
            Returns : None
        """
        self.ws = ws

    def __del__(self) -> None:
        """
            Delete the solver (what to delete)
            Args : None
            Returns : None
        """

    async def init(self,params = {}) -> dict:
        """
            Init the solver , until the function is just used to change the command line format
            Args : 
                params : dict
                    type : str # "astrometry" or "astap"
            Returns : dict
        """

    async def solve_image(self,params = {}) -> dict:
        """
            Solve the image and return the information
            Args:
                params : dict
                    filename : str # full path to the image
            Returns : dict
                ra : str # ra of the center of the image
                dec : str # dec of the center of the image
                starindex : int # number of stars in the image
        """

    async def get_template(self,params = {}) -> dict:
        """
            Get all of the template in specified folder and return a list of the templates
            Args :
                params : dict
                    path : str # full path to the template
            Returns : dict
                list : list # list of templates
        """

    async def scan_template(self, params = {}) -> dict:
        """
            Scan all the templates available and return a list of the templates to download
            Args : 
                params : dict
                    path : str # full path to the existing templates
            Returns : dict
        """

    async def download_template(self,params = {}) -> dict:
        """
            Download the specified template to specified folder
            Args : 
                params : dict
                    name : str # name of the template
                    folder : str # if null will choose the default folder
            Returns : dict
        """

    # #################################################################
    #
    # Astrometry functions
    #
    # #################################################################

    # #################################################################
    # Online API
    # #################################################################

    """
        Arguments:

        * ``session``: string, requried.  Your session key, required in all requests
        * ``url``: string, required.  The URL you want to submit to be solved
        * ``allow_commercial_use``: string: "d" (default), "y", "n": licensing terms
        * ``allow_modifications``: string: "d" (default), "y", "n", "sa" (share-alike): licensing terms
        * ``publicly_visible``: string: "y", "n"
        * ``scale_units``: string: "degwidth" (default), "arcminwidth", "arcsecperpix".  The units for the "scale_lower" and "scale_upper" arguments; becomes the "--scale-units" argument to "solve-field" on the server side.
        * ``scale_type``: string, "ul" (default) or "ev".  Set "ul" if you are going to provide "scale_lower" and "scale_upper" arguments, or "ev" if you are going to provide "scale_est" (estimate) and "scale_err" (error percentage) arguments.
        * ``scale_lower``: float.  The lower-bound of the scale of the image.
        * ``scale_upper``: float.  The upper-bound of the scale of the image.
        * ``scale_est``: float.  The estimated scale of the image.
        * ``scale_err``: float, 0 to 100.  The error (percentage) on the estimated scale of the image.
        * ``center_ra``: float, 0 to 360, in degrees.  The position of the center of the image.
        * ``center_dec``: float, -90 to 90, in degrees.  The position of the center of the image.
        * ``radius``: float, in degrees.  Used with ``center_ra``,``center_dec`` to specify that you know roughly where your image is on the sky.
        * ``downsample_factor``: float, >1.  Downsample (bin) your image by this factor before performing source detection.  This often helps with saturated images, noisy images, and large images.  2 and 4 are commonly-useful values.
        * ``tweak_order``: int.  Polynomial degree (order) for distortion correction.  Default is 2.  Higher orders may produce totally bogus results (high-order polynomials are strange beasts).
        * ``use_sextractor``: boolean.  Use the `SourceExtractor <http://www.astromatic.net/software/sextractor>`_ program to detect stars, not our built-in program.
        * ``crpix_center``: boolean.  Set the WCS reference position to be the center pixel in the image?  By default the center is the center of the quadrangle of stars used to identify the image.
        * ``parity``: int, 0, 1 or 2.  Default 2 means "try both".  0 means that the sign of the determinant of the WCS CD matrix is positive, 1 means negative.  The short answer is, "try both and see which one works" if you are interested in using this option.  It results in searching half as many matches so can be helpful speed-wise.
        * ``image_width``: int, only necessary if you are submitting an "x,y list" of source positions.
        * ``image_height``: int, ditto.
        * ``positional_error``: float, expected error on the positions of stars in your image.  Default is 1.
    """

