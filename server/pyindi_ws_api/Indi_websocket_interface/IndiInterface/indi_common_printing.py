import PyIndi
from PyIndi import BaseDevice, Property
from .indiClientDef import IndiClient
import traceback
from .basic_indi_state_str import strISState, strIPState


def get_str_all_device(indiclient: IndiClient):
    ret_string = ''
    dl = indiclient.getDevices()
    ret_string += "List of Device Properties\n"
    for one_device in dl:
        ret_string += str_single_device_all_properties(one_device)
    return ret_string


def str_single_device_all_properties(single_device: BaseDevice):
    ret_string = ''
    ret_string += "-- " + single_device.getDeviceName() + '\n'
    all_device_properties = single_device.getProperties()
    for one_device_property in all_device_properties:
        ret_string += str_single_property(one_device_property)
    return ret_string


def str_single_property(single_property: Property):
    ret_string = ''
    ret_string += "   > " + single_property.getName()

    if single_property.getType() == PyIndi.INDI_TEXT:
        ret_string += ' type text\n'
        tpy = single_property.getText()
        for t in tpy:
            ret_string += "       " + t.name + "(" + t.label + ")= " + t.text + '\n'
    elif single_property.getType() == PyIndi.INDI_NUMBER:
        ret_string += ' type number\n'
        tpy = single_property.getNumber()
        for t in tpy:
            ret_string += "       " + t.name + "(" + t.label + ")= " + str(t.value) + '\n'
    elif single_property.getType() == PyIndi.INDI_SWITCH:
        ret_string += ' type switch\n'
        tpy = single_property.getSwitch()
        for t in tpy:
            ret_string += "       " + t.name + "(" + t.label + ")= " + strISState(t.s) + '\n'
    elif single_property.getType() == PyIndi.INDI_LIGHT:
        ret_string += ' type light\n'
        tpy = single_property.getLight()
        for t in tpy:
            ret_string += "       " + t.name + "(" + t.label + ")= " + strIPState(t.s) + '\n'
    elif single_property.getType() == PyIndi.INDI_BLOB:
        ret_string += ' type blob\n'
        tpy = single_property.getBLOB()
        for t in tpy:
            ret_string += "       " + t.name + "(" + t.label + ")= <blob " + str(t.size) + " bytes>" + '\n'

    return ret_string


def get_str_one_device(indiclient: IndiClient, device_name):
    this_device = None
    try:
        if type(device_name) == str:
            this_device = indiclient.getDevice(device_name)
        else:
            this_device = device_name
    except TypeError:
        return 'Got Wrong device type! Please check input!'
    except:
        return traceback.format_exc()

    if this_device is not None:
        return str_single_device_all_properties(this_device)
    else:
        return 'Got Wrong device type!! Please check input!'


def get_str_one_property(indiclient: IndiClient, device_name, *args):
    this_device = None
    try:
        if type(device_name) == str:
            this_device = indiclient.getDevice(device_name)
        else:
            this_device = device_name
    except TypeError:
        return 'Got Wrong device type! Please check input!'
    except:
        return traceback.format_exc()

    if this_device is not None:
        ret_str = ''
        for one_property_name in args:
            try:
                this_property = this_device.getProperty(one_property_name)
                ret_str += str_single_property(this_property)
            except:
                ret_str += "       " + one_property_name + " is not a valid property name\n"
        return ret_str
    else:
        return 'Got Wrong device type!! Please check input!'

