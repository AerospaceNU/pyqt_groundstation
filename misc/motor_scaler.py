"""
Simple script to scale the thrust curve on a I350 motor
"""

import os


def rescale(motor_manufacturer, motor_name, scale_factor, openrocket_dir="/home/nathan/.openrocket/ThrustCurves"):
    source_name = f"{motor_manufacturer}_{motor_name}_Base"
    destination_name = f"{motor_manufacturer}_{motor_name}_Scaled"

    source_path = os.path.join(openrocket_dir, f"{source_name}.eng")
    dest_path = os.path.join(openrocket_dir, f"{destination_name}.eng")

    file = open(source_path)
    lines = file.readlines()
    file.close()

    new_lines = []

    for line in lines:
        if ";" in line:
            new_lines.append(line)
        elif f"{motor_name}_Base" in line:
            new_lines.append(line.replace(f"{motor_name}_Base", f"{motor_name}_Scaled"))
        else:
            vals = line.strip().split(" ")
            thrust = float(vals[-1]) * scale_factor

            new_line = f"   {vals[0]}     {thrust:.2f}\n"
            new_lines.append(new_line)

    new_file = open(dest_path, "w")
    new_file.writelines(new_lines)
    new_file.close()


if __name__ == '__main__':
    # rescale("Cesaroni", "I360", 0.8)
    rescale("AeroTech", "G76G", 0.8)
