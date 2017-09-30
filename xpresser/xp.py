#
# Copyright (c) 2010 Canonical
#
# Written by Gustavo Niemeyer <gustavo@niemeyer.net>
#
# This file is part of the Xpresser GUI automation library.
#
# Xpresser is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3,
# as published by the Free Software Foundation.
#
# Xpresser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import time

from xpresser import xutils
from xpresser.image import Image
from xpresser.errors import XpresserError
from xpresser.imagedir import ImageDir
from xpresser.imagematch import ImageMatch
from xpresser.opencvfinder import OpenCVFinder


class ImageNotFound(XpresserError):
    """Exception raised when a request to find an image doesn't succeed."""


class Xpresser(object):

    def __init__(self):
        self._imagedir = ImageDir()
        self._imagefinder = OpenCVFinder()

    def load_images(self, path):
        self._imagedir.load(path)

    def get_image(self, name):
        return self._imagedir.get(name)

    def _compute_focus_point(self, args):
        if (len(args) == 2 and
            isinstance(args[0], (int, long)) and
            isinstance(args[1], (int, long))):
            return args
        elif len(args) == 1:
            if type(args[0]) == ImageMatch:
                match = args[0]
            else:
                match = self.find(args[0])
            return match.focus_point

    def click(self, *args):
        """Click on the position specified by the provided arguments.

        The following examples show valid ways of specifying the position:

            xp.click("image-name")
            xp.click(image_match)
            xp.click(x, y)
        """
        xutils.click(*self._compute_focus_point(args))

    def right_click(self, *args):
        """Right-click on the position specified by the provided arguments.

        The following examples show valid ways of specifying the position:

            xp.right_click("image-name")
            xp.right_click(image_match)
            xp.right_click(x, y)
        """
        xutils.right_click(*self._compute_focus_point(args))

    def double_click(self, *args):
        '''Double clicks over the position specified by arguments

        The following examples show valid ways of specifying the position:
             xp.double_click("image-name")
             xp.double_click(image_match)
             xp.double_click(x, y)
        '''
        xutils.double_click(*self._compute_focus_point(args))

    def hover(self, *args):
        """Hover over the position specified by the provided arguments.

        The following examples show valid ways of specifying the position:

            xp.hover("image-name")
            xp.hover(image_match)
            xp.hover(x, y)
        """
        xutils.hover(*self._compute_focus_point(args))

    def find(self, image, timeout=10):
        """Given an image or an image name, find it on the screen.

        @param image: Image or image name to be searched for.
        @return: An ImageMatch instance, or None.
        """
        if isinstance(image, basestring):
            image = self._imagedir.get(image)
        wait_until = time.time() + timeout
        while time.time() < wait_until:
            screenshot_image = xutils.take_screenshot()
            match = self._imagefinder.find(screenshot_image, image)
            if match is not None:
                return match
        raise ImageNotFound(image)

    def wait(self, image, timeout=30):
        """Wait for an image to show up in the screen up to C{timeout} seconds.

        @param image: Image or image name to be searched for.
        @return: An ImageMatch instance, or None.
        """
        self.find(image, timeout)

    def type(self, string, hold=0.4):
        """Enter the string provided as if it was typed via the keyboard.
        """
        xutils.type(string, hold)
