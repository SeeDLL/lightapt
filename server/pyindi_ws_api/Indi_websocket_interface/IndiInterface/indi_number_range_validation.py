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