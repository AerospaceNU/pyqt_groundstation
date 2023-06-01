"""
String constants that are used throughout the code
"""


class Constants:
    altitude_key = "fcb_altitude"
    latitude_key = "fcb_latitude"
    longitude_key = "fcb_longitude"
    gps_alt_key = "gps_alt"
    vertical_speed_key = "v_speed"
    acceleration_key = "accel_z"
    fcb_state_key = "fcb_state_text"
    fcb_state_number_key = "fcb_state_number"
    pyro_continuity = "pyro_continuity"
    pyro_fire_status = "pyro_status"
    flash_usage = "flash_usage"
    software_version_key = "software_version"
    serial_number_key = "board_serial_number"
    timestamp_ms_key = "time_stamp_ms"
    callsign_key = "callsign"
    temperature_key = "temperature"
    gps_time_key = "gps_time"
    ground_speed_key = "ground_speed"
    course_over_ground_key = "course_over_ground"
    climb_rate_key = "climb_rate"
    gps_sats_key = "gps_sats"
    bluetooth_connection_key = "ble_client"
    status_source = "status"

    orientation_quaternion_key = "orientation_quaternion"  # W X Y Z
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

    angle_vertical_key = "angle_vertical"

    barometer_pressure_key = "barometer_pressure"
    barometer_pressure_2_key = "barometer_2_pressure"
    press_ref_key = "press_ref"
    ground_elevation_key = "ground_elev"
    ground_temp_key = "ground_temp"
    main_cut_alt_key = "Main Alt (m)"
    pitot_ducer_press_key = "pitot_ducer_press"

    ground_station_latitude_key = "gs_lat"
    ground_station_longitude_key = "gs_lon"
    ground_station_altitude_key = "gs_alt"
    ground_station_pressure_key = "gs_baro"
    ground_station_temperature_key = "gs_temp"

    backup_gps_latitude = "egg_finder_latitude"
    backup_gps_longitude = "egg_finder_longitude"
    backup_gps_altitude = "egg_finder_altitude"
    egg_finder_age = "egg_finder_age"

    laptop_disk_usage_key = "laptop_disk"
    laptop_cpu_usage_key = "laptop_cpu"
    laptop_ram_usage_key = "laptop_ram"
    laptop_battery_percent_key = "laptop_battery_percent"
    laptop_battery_charging_key = "laptop_charging"

    fcb_battery_voltage = "fcb_battery_voltage"
    fcb_memory_usage = "fcb_memory"

    prop_battery_voltage = "prop_battery_voltage"
    prop_command_key = "prop_command"

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
    cli_interface_key = "cli_interface"
    cli_interface_usb_command_key = "cli_interface_usb"
    cli_interface_usb_result_key = "cli_interface_usb_result"
    cli_interface_usb_command_running = "fcb_cli_command_running"
    cli_string_key = "cli_string"
    cli_flights_list_key = "fcb_flights_list"
    new_cli_message_key = "new_cli_message"
    new_usb_cli_message_key = "new_usb_cli_message"
    new_offload_flight_saved_key = "new_offload_flight_saved"
    diagnostics_key = "diagnostics"

    invalid_fcb_state_name = "Invalid FCB State"
    fcb_state_names = [
        "Cli Erase Flash",
        "CLI Offload",
        "Ascent",
        "Descent",
        "Initialize",
        "Post Flight",
        "Pre Flight",
        "Sim Temp State",
        "NUM_STATES",
        "UNKNOWN",
    ]

    PREFLIGHT_STATE_INDEX = 6
    POWERED_ASCENT_STATE_INDEX = 2
    COAST_TO_APOGEE_INDEX = 2
    DROGUE_DESCENT_INDEX = 3
    MAIN_DESCENT_INDEX = 3
    END_STATE_INDEX = 5
    UNKNOWN_STATE_INDEX = 9

    MAX_PYROS = 6

    map_tile_manager_key = "map_tile_manager"
    enable_module_key = "enable_module"
    module_data_key = "module_data"
    set_recorded_data_callback_id = "set_recorded_data_and_interface"

    class InterfaceNames:
        ground_station_data = "Serial Ground Station"
        egg_finder = "Egg Finder Radio"
        fcb_offload = "FCB Offload"
        android_bluetooth = "Android Phone Bluetooth"
        text_speech = "Text To Speech"
        laptop_status = "Laptop Status Monitor"
        local_sim = "Local Simulation"
        ground_station_recorded_data = "Ground Station Recorded Data"
        fake_flight = "Fake Flight"
        random_data = "Random Data for Debugging"
        map_interface = "Map Interface"
        prop_websocket = "Prop Websocket Interface"

    # Line cutter stuff
    MAX_LINE_CUTTER_ID_VALID = 50

    line_cutter_number_key = "line_cutter_number"
    line_cutter_state_key = "state"
    delta_altitude_key = "delta_alt"
    battery_voltage_key = "battery_voltage"
    line_cutter_cut_1 = "cut_1"
    line_cutter_cut_2 = "cut_2"
    line_cutter_current_sense_key = "current_sense"
    photoresistor_key = "photoresistor"
    photoresistor_threshold_key = "photoresistor_threshold"

    class OffloadConstants:
        altitude_key = "pos_z"
        latitude_key = "gps_lat"
        longitude_key = "gps_long"
        gps_alt_key = "gps_alt"
        vertical_speed_key = "vel_z"
        # ground_speed_key = "gps_"

        # TODO average both
        acceleration_x_key = "imu1_accel_x_real"
        acceleration_y_key = "imu1_accel_y_real"
        acceleration_z_key = "imu1_accel_z_real"
        rotational_velocity_x_key = "imu1_gyro_x_real"
        rotational_velocity_y_key = "imu1_gyro_y_real"
        rotational_velocity_z_key = "imu1_gyro_z_real"
        magnetometer_x_key = "imu1_mag_x_real"
        magnetometer_y_key = "imu1_mag_y_real"
        magnetometer_z_key = "imu1_mag_z_real"

        barometer_pressure_key = "baro1_pres"
        barometer_pressure_2_key = "baro2_pres"

        fcb_state_number_key = "state"

    @staticmethod
    def makeLineCutterString(line_cutter_number, line_cutter_key):
        return "line_cutter_{0}_{1}".format(line_cutter_number, line_cutter_key)

    @staticmethod
    def makeDiagnosticsKey(source_name, page_name):
        return f"{Constants.diagnostics_key}/{source_name}/{page_name}"
