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
from PyIndi import INDI_SWITCH


def turn_on_first_swtich(pyindi_swtich: INDI_SWITCH):
    pyindi_swtich[0].s = PyIndi.ISS_ON
    pyindi_swtich[1].s = PyIndi.ISS_OFF
    return pyindi_swtich


def turn_on_second_swtich(pyindi_swtich: INDI_SWITCH):
    pyindi_swtich[0].s = PyIndi.ISS_OFF
    pyindi_swtich[1].s = PyIndi.ISS_ON
    return pyindi_swtich


def turn_on_multiple_switch_by_index(pyindi_switch: INDI_SWITCH, turn_one_index: int):
    for (index, one_switch) in enumerate(pyindi_switch):
        if index == turn_one_index:
            one_switch.s = PyIndi.ISS_ON
        else:
            one_switch.s = PyIndi.ISS_OFF
    return pyindi_switch


def get_multiple_switch_info(pyindi_switch: INDI_SWITCH):
    ret_struct = {
        'value': None,
        'selections': []
    }
    for (index, one_switch) in enumerate(pyindi_switch):
        ret_struct['selections'].append(one_switch.name)
        if one_switch.s == PyIndi.ISS_ON:
            ret_struct['value'] = one_switch.name
    return ret_struct
