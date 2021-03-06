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

import gi
gi.require_version('Gdk', '3.0')

import mss
import numpy
import pyatspi
import cv2
import types
import time
from xpresser.image import Image
from tempfile import NamedTemporaryFile
from gi.repository import Gdk

specialkeys = {'<Ctrl>' : 37, "<Shift>" : 50, "<Alt>" : 64, "<Meta>" :  133,
               '<Tab>' : 23, '<Super>' : 133, '<Fn>' : 151, '<PgUp>' : 112,
               '<PgDn>' : 117, '<Delete>' : 119, '<Home>' : 110, '<Esc>' : 9,
               '<F1>' : 67, '<F2>' : 68, '<F3>' : 69, '<F4>' : 70, '<F5>' : 71,
               '<F6>' : 72, '<F7>' : 73, '<F8>' : 74, '<F9>' : 75, '<F10>' : 76,
               '<F11>' : 95, '<F12>' : 96, '<Enter>' : 36}


def click(x, y):
    pyatspi.Registry.generateMouseEvent(x, y, pyatspi.MOUSE_B1C)

def right_click(x, y):
    pyatspi.Registry.generateMouseEvent(x, y, pyatspi.MOUSE_B3C)

def double_click(x, y):
    pyatspi.Registry.generateMouseEvent(x, y, pyatspi.MOUSE_B1D)

def hover(x, y):
    pyatspi.Registry.generateMouseEvent(x, y, pyatspi.MOUSE_ABS)

def type(string, hold):
    if isinstance(string, types.ListType):
        keys_to_press = []
        for string_part in string:
            if string_part in specialkeys:
                keys_to_press.append(specialkeys[string_part])
                __press_key(keys_to_press[-1])
            else:
                __type_standard(string_part)
        keys_to_press.reverse()
        #hold the key long enough to constitute a hold, not a tap
        time.sleep(hold)
        for keys in keys_to_press:
            __release_key(keys)
    else:
        __type_standard(string)

def __type_standard(string):        
    for char in string:
        keyval = Gdk.unicode_to_keyval(ord(char))
        pyatspi.Registry.generateKeyboardEvent(keyval, None, pyatspi.KEY_SYM)

def __press_key(keycode):
    pyatspi.Registry.generateKeyboardEvent(keycode, None, pyatspi.KEY_PRESS)

def __release_key(keycode):
    pyatspi.Registry.generateKeyboardEvent(keycode, None, pyatspi.KEY_RELEASE)

def take_screenshot():
    window = Gdk.get_default_root_window()
    surface = Gdk.cairo_create(window).get_target()
    with NamedTemporaryFile(prefix='xpresser_', suffix='.png') as f:
        surface.write_to_png(f.name)
        with mss.mss() as sct:
            numpy.array(sct.shot(output="monitor-1.png"))
            opencv_image = cv2.imread('monitor-1.png')
            height, width, channels = opencv_image.shape
    return Image("monitor-1.png", array=opencv_image,
                 width=width, height=height)
