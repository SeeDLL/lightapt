telescope data struct and instruction definition
=========================================================

private data saved by websocket interface
-------------------------------------------------

* longitude
* latitude
* elevation

initial after connection
+++++++++++++++++++++++++++++

* can_set_max_alt   
* can_park
* can_home
* can_track_speed
* can_slew_speed
* can_guide_speed

minimum instruction set
----------------------------

* set_long_lat
* get_static_info       get telescope static information which cannot be changed
* get_set_params        get important setting params
* get_all_params
* set_param
* get_real_time_info    get ra dec ha dec alt az
* goto                  goto ra dec
* goto_ha_dec
* goto_alt_az
* set_track_rate
* start_track
* stop_track
* park
* unpark
* set_park
* abort
* home
* at_home
* set_track_speed
* set_slew_speed
* set_guiding_speed
* move_direction
