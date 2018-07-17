#
# A brief script to extract metadeta from image files
#

import exifread
import fnmatch
import os
import csv


def convert(coord):
    """ Convert the instance to actual floats. Returns coords as a list"""

    # Covert instance to string then split it up
    coord = str(coord)
    coord_strip = coord.strip("[]")
    coord_split = coord_strip.split(", ")
    decimal = coord_split[2].split("/")

    if len(decimal) == 2:
        decimal = float(decimal[0]) / float(decimal[1])
    else:
        decimal = float(decimal[0])

    coord = [float(coord_split[0]), float(coord_split[1]), decimal]

    return coord


def main():

    match_list = []
    match_folder = []
    top_folder = r"C:\Users\William.Yingling\Scripts\ArcMap_Projects\Mosaicking\Run02\\"

    # find all matches in the sub dirs
    for root, dirnames, filenames in os.walk(top_folder):
        for filename in fnmatch.filter(filenames, '*.jpg'):
            match_list.append(os.path.join(root, filename))
            if root not in match_folder:
                match_folder.append(root)

    # Loop through available folders,
    # then create a csv containing metadata (the gps coords)
    # of the images within that folder
    for path in match_folder:

        exif_file = path + "\Exif_data.csv"
        print "Working in " + path

        files_in_folder = []

        # looks for files only in path
        for i in match_list:
            if (path in i) and (i not in files_in_folder):
                files_in_folder.append(i)

        # open new file in each dir
        with open(exif_file, "wb") as ef:
            writer = csv.writer(ef, delimiter=',')
            header = ["Image_Path", "Latitude", " ", " ", "Longitude"]
            writer.writerow(header)

            # extract GPS from each image
            for file_ in files_in_folder:

                # read meta data
                f = open(file_, 'rb')
                tags = exifread.process_file(f)
                f.close()

                lat_key = "GPS GPSLatitude"
                longi_key = "GPS GPSLongitude"

                # check and define lat and long
                if (lat_key in tags.keys()) and (longi_key in tags.keys()):

                    lat = tags[lat_key]
                    longi = tags[longi_key]

                    # convert the instance to a list of coords
                    lat = convert(lat)
                    longi = convert(longi)

                else:
                    # if there is not gps data, dont do anything
                    continue

                # write data to the file
                line = [file_] + lat + longi
                writer.writerow(line)

    print "Exif data extraction successful!"

if __name__ == '__main__':
    main()

# Will Yingling
# Biological Science Technician, USDA
# August 2017
