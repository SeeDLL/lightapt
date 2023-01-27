camera data structure and instruction definition
===================================================

private data saved by websocket interface
----------------------------------------------

* fits_save_path
    file save path, can be changed manually
* subframe_counting
    counting for subframes if there is no outer counting
* save_file_name_pattern
    usage see comment in code
* in_exposure
    flag noting whether this device is in exposure

initial after connection 
+++++++++++++++++++++++++++++

* can_cool
* has_fan
* has_heater
* has_binning
* gain_type

minimum instruction set
---------------------------
=======================                     ======================                                  =============
method name                                 parameters                                              return type
=======================                     ======================                                  =============
* set_cool_target_temperature               [target_temperature]                                    message
* get_static_info                           no parameters needed                                    message
* get_set_params                            no parameters needed                                    message
* get_real_time_info                        no parameters needed                                    message
* start_cool_camera                         no parameters needed                                    message
* stop_cool_camera                          no parameters needed                                    message
* start_fan                                 no parameters needed                                    message
* stop_fan                                  no parameters needed                                    message
* start_tc_heat                             no parameters needed                                    message
* stop_tc_heat                              no parameters needed                                    message
* start_single_exposure                     [exposure_time, subframe_count(optional)]               message
* abort_exposure                            no parameters needed                                    message

* set_save_file_path
* change_save_file_name_pattern
=======================                     ======================                                  =============