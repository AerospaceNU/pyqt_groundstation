"""
String constants that are used throughout the code
"""


class Constants:
    altitude_key = "altitude"
    latitude_key = "latitude"
    longitude_key = "longitude"
    gps_alt_key = "gps_alt"
    vertical_speed_key = "v_speed"
    acceleration_key = "accel_z"
    fcb_state_key = "fcb_state"
    pyro_continuity = "pyro_continuity"
    software_version_key = "software_version"
    serial_number_key = "board_serial_number"
    timestamp_ms_key = "time_stamp_ms"
    callisgn_key = "callsign"
    temperature_key = "temperature"
    gps_time_key = "gps_time"
    ground_speed_key = "ground_speed"
    course_over_ground_key = "course_over_ground"
    climb_rate_key = "climb_rate"
    gps_sats_key = "gps_sats"
    bluetooth_connection_key = "ble_client"
    status_source = "status"

    orientation_quaternion_key = "orientation_quaternion"
    orientation_rpy_key = "orientation_rpy"
    rotational_velocity_key = "rotational_velocity"
    acceleration_vector_key = "acceleration_vector"
    magnetic_vector_key = "magnetic_vector"

    roll_position_key = "roll"
    pitch_position_key = "pitch"
    yaw_position_key = "yaw"

    rotational_velocity_x_key = "rot_vel_x"
    rotational_velocity_y_key = "rot_vel_y"
    rotational_velocity_z_key = "rot_vel_z"

    acceleration_x_key = "accel_x"
    acceleration_y_key = "accel_y"
    acceleration_z_key = "accel_z"

    magnetometer_x_key = "magnetic_field_x"
    magnetometer_y_key = "magnetic_field_y"
    magnetometer_z_key = "magnetic_field_z"

    ground_station_latitude_key = "gs_lat"
    ground_station_longitude_key = "gs_lon"
    ground_station_altitude_key = "gs_alt"
    ground_station_pressure_key = "gs_baro"
    ground_station_temperature_key = "gs_temp"

    laptop_disk_usage_key = "laptop_disk"
    laptop_cpu_usage_key = "laptop_cpu"
    laptop_ram_usage_key = "laptop_ram"
    laptop_battery_percent_key = "laptop_battery_percent"
    laptop_battery_charging_key = "laptop_charging"

    barometer_pressure_key = "barometer_pressure"
    barometer_pressure_2_key = "baro_2_pressure"

    fcb_battery_voltage = "fcb_battery_voltage"
    fcb_memory_usage = "fcb_memory"

    prop_battery_voltage = "prop_battery_voltage"
    line_cutter_1_voltage = "line_cutter_1_voltage"
    line_cutter_2_voltage = "line_cutter_2_voltage"

    message_age_key = "message_age"
    message_time_key = "message_time"
    rssi_key = "rssi"
    rssi_val_key = "rssi_val"  # The float val
    lqi_key = "lqi"
    crc_key = "crc"
    radio_id_key = "radio_id"
    radio_id_string = "radio_name"
    loop_time_key = "gui_loop_time"

    primary_annunciator = "annunciator_1"
    primary_reconfigure = "primary_reconfigure"
    raw_message_data_key = "raw_message_data"
    cli_interface_key = "cli_interface"
    cli_string_key = "cli_string"

    invalid_fcb_state_name = "Invalid FCB State"
    fcb_state_names = ["Cli Calibrate",
                       "Cli Config",
                       "Cli Erase Flash",
                       "Cli Help",
                       "Cli Main",
                       "Cli Offload",
                       "Cli Sense",
                       "Ascent",
                       "Drogue Descent N",
                       "Initialize",
                       "Main Descent",
                       "Post Flight",
                       "Pre Flight",
                       "Shutdown",
                       "NUM_STATES",
                       "UNKNOWN"]

    PREFLIGHT_STATE_INDEX = 13
    POWERED_ASCENT_STATE_INDEX = 7
    COAST_TO_APOGEE_INDEX = 7
    DROGUE_DESCENT_INDEX = 8
    MAIN_DESCENT_INDEX = 10
    END_STATE_INDEX = 11
    UNKNOWN_STATE_INDEX = 16

    MAX_PYROS = 6
