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
    for (index, one_switch) in pyindi_switch:
        if index == turn_one_index:
            one_switch.s = PyIndi.ISS_ON
        else:
            one_switch.s = PyIndi.ISS_OFF
    return pyindi_switch