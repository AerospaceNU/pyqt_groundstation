"""
String constants that are used throughout the code
"""


class Constants:
    altitude_key = "altitude"
    latitude_key = "latitude"
    longitude_key = "longitude"
    gps_alt_key = "gps_alt"
    vertical_speed_key = "v_speed"
    acceleration_key = "acceleration"
    fcb_state_key = "fcb_state"
    pyro_continuity = "pyro_continuity"
    software_version_key = "software_version"
    timestamp_ms_key = "time_stamp_ms"
    callisgn_key = "callsign"
    temperature_key = "temperature"
    gps_time_key = "gps_time"
    ground_speed_key = "ground_speed"
    climb_rate_key = "climb_rate"
    gps_sats_key = "gps_sats"
    bluetooth_connection_key = "ble_client"

    ground_station_latitude_key = "gs_lat"
    ground_station_longitude_key = "gs_lon"
    ground_station_altitude_key = "gps_alt"

    barometer_pressure_key = "barometer_pressure"

    fcb_battery_voltage = "fcb_battery_voltage"
    fcb_memory_usage = "fcb_memory"

    prop_battery_voltage = "prop_battery_voltage"
    line_cutter_1_voltage = "line_cutter_1_voltage"
    line_cutter_2_voltage = "line_cutter_2_voltage"

    message_age_key = "message_age"
    rssi_key = "rssi"
    lqi_key = "lqi"
    crc_key = "crc"
    raw_message_data_key = "raw_message_data"

    invalid_fcb_state_name = "Invalid FCB State"
    fcb_state_names = ["Cli Calibrate",
                       "Cli Config",
                       "Cli Erase Flash",
                       "Cli Help",
                       "Cli Main",
                       "Cli Offload",
                       "Cli Sense",
                       "Coast Ascent",
                       "Drogue Descent N",
                       "Initialize",
                       "Main Descent",
                       "Post Flight",
                       "Powered Ascent",
                       "Pre Flight",
                       "Shutdown",
                       "NUM_STATES",
                       "UNKNOWN"]
