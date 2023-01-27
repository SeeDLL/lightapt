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

from PyIndi import PropertyNumber

def check_number_range(indi_number: PropertyNumber, value_index: int, tobe_set_value):
    if value_index >= len(indi_number):
        return False
    value_max = indi_number[value_index].max
    value_min = indi_number[value_index].min
    if value_min <= tobe_set_value <= value_max:
        return True
    else:
        return False


def indi_number_single_get_value(indi_number):
    return {
        'name': indi_number.name,
        'value': indi_number.value,
        'max': indi_number.max,
        'min': indi_number.min
    }