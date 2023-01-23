import PyIndi
from .basic_indi_state_str import json_ISState, json_IPState


def indi_property_2_json(indi_property):
    ret_struct = {}
    if indi_property.getType() == PyIndi.INDI_TEXT:
        ret_struct['type'] = 'text'
        for one_ in indi_property:
            ret_struct[one_.name] = one_.text
    if indi_property.getType() == PyIndi.INDI_NUMBER:
        ret_struct['type'] = 'number'
        for one_ in indi_property:
            ret_struct[one_.name] = one_.value
    if indi_property.getType() == PyIndi.INDI_SWITCH:
        ret_struct['type'] = 'switch'
        for one_ in indi_property:
            ret_struct[one_.name] = json_ISState(one_.s)
    if indi_property.getType() == PyIndi.INDI_LIGHT:
        ret_struct['type'] = 'light'
        for one_ in indi_property:
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
