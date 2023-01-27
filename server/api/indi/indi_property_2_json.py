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

import PyIndi
from .basic_indi_state_str import json_ISState, json_IPState

def indi_property_2_json(indi_property):
    ret_struct = {
        'name': indi_property.getName()
    }
    if indi_property.getType() == PyIndi.INDI_TEXT:
        ret_struct['type'] = 'text'
        this_p = indi_property.getText()
        for one_ in this_p:
            ret_struct[one_.name] = one_.text
    if indi_property.getType() == PyIndi.INDI_NUMBER:
        ret_struct['type'] = 'number'
        this_p = indi_property.getNumber()
        for one_ in this_p:
            ret_struct[one_.name] = one_.value
    if indi_property.getType() == PyIndi.INDI_SWITCH:
        ret_struct['type'] = 'switch'
        this_p = indi_property.getSwitch()
        for one_ in this_p:
            ret_struct[one_.name] = json_ISState(one_.s)
    if indi_property.getType() == PyIndi.INDI_LIGHT:
        ret_struct['type'] = 'light'
        this_p = indi_property.getLight()
        for one_ in this_p:
            ret_struct[one_.name] = json_IPState(one_.s)
    return ret_struct


def indi_keyword_2_json(indi_device, *args):
    # transfer indi device by keyword list to json
    ret_list = []
    for one_property_name in args:
        this_property = indi_device.getProperty(one_property_name)
        if (this_property):
            ret_list.append(indi_property_2_json(this_property))
        else:
            ret_list.append(None)
    return ret_list
