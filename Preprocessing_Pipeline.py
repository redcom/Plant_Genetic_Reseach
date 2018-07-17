import numpy as np
import csv
import sys
import os


def read_file(file_name):

    x = open(file_name, "r")
    data_lines = x.readlines()
    trait_data = []

    for x in data_lines:

        y = x.split()

        # safety for bad lines
        if len(y) == 0:
            continue

        trait_data.append(y)

    return trait_data


def find_gps(gps_data):

    coords = {}

    for line in gps_data[1:]:

        if "N" not in line:
            continue

        line_index = line.index("N")
        lat_index = line_index - 1
        long_index = line_index + 1

        if line[0] not in coords:

            coord_value = [line[lat_index], line[long_index]]

            coords.update({line[0]: coord_value})

    return coords


def merge_gps(new_trait, trait_data, coords):

    merge_data = []

    for t in trait_data[1:]:

        id_ = t[0]
        t += coords[id_]

        merge_data.append(t)

    header = trait_data[0] + ["Latitude", "Longitude"]

    with open(new_trait, "wb") as nt:
        csvwriter = csv.writer(nt, delimiter=",")

        csvwriter.writerow(header)

        for line in merge_data:
            csvwriter.writerow(line)

    return


def main():

    gps_file = r"E:\htp\Preprocessing_Pipeline\GPS_RawData.txt"
    irt_file = r"E:\htp\Preprocessing_Pipeline\IRT_RawData.txt"
    new_irt = r"E:\htp\Preprocessing_Pipeline\IRT_GPS.csv"

    gps_data = read_file(gps_file)
    irt_data = read_file(irt_file)

    coords = find_gps(gps_data)

    merge_gps(new_irt, irt_data, coords)


main()
