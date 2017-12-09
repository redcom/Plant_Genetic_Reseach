#!/usr/bin/python
#
# Adapted from the tutorial found at
# http://plantcv.readthedocs.io/en/latest/vis_tutorial/
#

import os
import sys
import numpy as np
import fnmatch
import argparse
import plantcv as pcv
import exifread
import csv
import tkFileDialog as fd
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import LatLongUTMconversion
import imutils
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tkFileDialog as fd
import scipy.misc as sp
from multiprocessing import Pool
import random


def calculate_ndvi(r, g, b):
    """ NDVI is the (NIR - Red) / (NIR + Red) """

    nir = r
    red = g

    ndvi = (nir - red) / (nir + red)

    return ndvi


def calculate_vari(r, g, b):
    """ Visible Atmospherically Ressitant Index to measure 'how green' """

    vari = (g - r) / (g + r - b)

    return vari


def calculate_tgi(r, g, b):
    """ Triangular Greenness Index to estimate leaf chlorophyll """

    # the  div g component is to normailze the green signal
    tgi = (g - 0.39*r - 0.61*b) / g

    #tgi = -0.5 * ((670. - 480.)*(r - g) - (670. - 550.)*(r - b))

    return tgi


def calculate_ngrdi(r, g, b):
    """ Normalized Green Red Difference Index. Also NGBDI or NDGI"""

    ngrdi = (g - r) / (g + r)

    return ngrdi


def calculate_gli(r, g, b):
    """ Green Leaf Index """

    gli = (2*g - r - b) / (2*g + r + b)

    return gli


def check_ndvi(ndvi):

    if ndvi >= 0. and ndvi <= 1.:
        return True

    return False


def rgb_filter(red, green, blue):
    """ Run a STDev filter. """

    red_mean = np.mean(red)
    red_stdev = np.std(red)
    green_mean = np.mean(green)
    green_stdev = np.std(green)
    blue_mean = np.mean(blue)
    blue_stdev = np.std(blue)

    red_min = red_mean - red_stdev
    red_max = red_mean + red_stdev
    green_min = green_mean - green_stdev
    green_max = green_mean + green_stdev
    blue_min = blue_mean - blue_stdev
    blue_max = blue_mean + blue_stdev

    red_trim = red[(red > red_min) & (red < red_max) &
                   (green > green_min) & (green < green_max) &
                   (blue > blue_min) & (blue < blue_max)]

    green_trim = green[(red > red_min) & (red < red_max) &
                       (green > green_min) & (green < green_max) &
                       (blue > blue_min) & (blue < blue_max)]

    blue_trim = blue[(red > red_min) & (red < red_max) &
                     (green > green_min) & (green < green_max) &
                     (blue > blue_min) & (blue < blue_max)]

    return red_trim, green_trim, blue_trim


def read_exif(exif_files):

    img_utm = {}

    for exif in exif_files:
        with open(exif, "rb") as ex:
            reader = list(csv.reader(ex, delimiter=','))

        # Take out header
        reader.pop(0)

        for row in reader:

            #img_info[row[0]] = [float(row[3]), float(row[4])]
            img_utm[row[0]] = [float(row[5]), float(row[6])]

    return img_utm  # img_path, lat, longi


def read_boxes(box_data):

    with open(box_data, "rb") as bd:
        reader = list(csv.reader(bd, delimiter=','))

    reader.pop(0)

    seed_box = {}
    seed_id = []

    for row in reader:

        if row[4] not in seed_id and row[4] != "Br":
            seed_id.append(row[4])
        if row[3] not in seed_id and row[4] == "Br":
            seed_id.append(row[3])

    for i in range(len(seed_id)):
        lat = []
        longi = []

        for row in reader:
            if row[4] == seed_id[i] or row[3] == seed_id[i]:

                coords = list(LatLongUTMconversion.LLtoUTM(23, float(row[0]), float(row[1])))[1:]

                lat.append(float(coords[0]))
                longi.append(float(coords[1]))

        lat_max = round(max(lat), 6)
        lat_min = round(min(lat), 6)

        longi_max = round(max(longi), 6)
        longi_min = round(min(longi), 6)

        lat_avg = (lat_max + lat_min) / 2.
        longi_avg = (longi_max + longi_min) / 2.

        if len(seed_id[i]) > 8:
            seed_id[i] = "Br_" + seed_id[i]

        seed_box[seed_id[i]] = [lat_avg, longi_avg]

    return seed_box, seed_id


def diff_calc(lat, longi, si_coords):
    """Calc the difference between the plot avg and the seed box avg"""

    lat_diff = abs(lat - si_coords[0])
    longi_diff = abs(longi - si_coords[1])

    diff = (lat_diff**2 + longi_diff**2)**0.5

    return diff


def diff_calc_utm_x(lat, longi, si_coords):
    """Calc the difference between the plot avg and the seed box avg"""

    diff = abs(lat - si_coords[0])

    return diff


def diff_calc_utm_y(longi, si_coords):
    """Calc the difference between the plot avg and the seed box avg"""

    diff = abs(longi - si_coords[1])

    return diff


def assign_plot(top_folder, groups_of_plot_paths, calcd_pir, calcd_dist):

    img_id = []

    for rang in range(len(groups_of_plot_paths)):
        for plot in range(len(groups_of_plot_paths[rang])):
            for img in range(len(groups_of_plot_paths[rang][plot])):

                image = groups_of_plot_paths[rang][plot][img]
                image_plot = calcd_pir[rang][plot]
                diff = calcd_dist[rang][plot]

                img_info = [image, image_plot, diff]

                img_id.append(img_info)

    assigned_plot = top_folder + "Plot_Match.csv"

    with open(assigned_plot, "wb") as ap:
        writer = csv.writer(ap, delimiter=",")

        for assignment in img_id:
            writer.writerow(assignment)

    return img_id


def group_plots(img_path, dirt, image_ranges):
    """Group the plots together with dirt separating plots."""

    groups_of_plot_paths = []
    plot_path = []
    range_paths = []

    for r in range(len(image_ranges)):

        for path in image_ranges[r]:

            if path in dirt and len(plot_path) > 0:

                range_paths.append(plot_path)
                plot_path = []

            elif path not in dirt:
                plot_path.append(path)

        if plot_path not in range_paths and len(plot_path) > 0:
            range_paths.append(plot_path)

        if range_paths not in groups_of_plot_paths and len(range_paths) > 0:

            groups_of_plot_paths.append(range_paths)
            range_paths = []
            plot_path = []

    return tuple(groups_of_plot_paths)


def group_plots_ra(img_path, dirt, image_ranges):
    """ Group the plots together with dirt separating plots. """

    groups_of_plot_paths = []
    plot_path = []

    for path in img_path:

        if path in dirt and len(plot_path) > 0:
            groups_of_plot_paths.append(plot_path)
            plot_path = []

        elif path not in dirt:
            plot_path.append(path)

    if plot_path not in groups_of_plot_paths and len(plot_path) > 0:
        groups_of_plot_paths.append(plot_path)

    return groups_of_plot_paths


def avg_plots(groups_of_plot_paths, img_info):
    """Avg the images within the plots"""

    avgs = []

    # extract a lat long from images and avg them over the plot
    for rang in groups_of_plot_paths:

        range_avgs = []

        for plot in rang:

            lats = []
            longs = []

            for image in plot:

                coords = img_info[image]
                lats.append(coords[0])
                longs.append(coords[1])

            avg_lat = sum(lats) / len(lats)
            avg_long = sum(longs) / len(longs)

            range_avgs.append([avg_lat, avg_long])

        avgs.append(range_avgs)

    print avgs, len(avgs)

    return tuple(avgs)


# Mike's tidbit
def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item.

    Also converts the GPS Tags
    """

    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data


# Mike's tidbit
def _get_if_exist(data, key):

    if key in data:
        return data[key]

    return None


# Mike's tidbit
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates

    stored in the EXIF to degress in float format
    """

    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


# Mike's tidbit.  It will take the Lat/Long
# information from the images and convert it
# to UTM Lat/Long which is used in QGIS or any mapping program.
# It calls the LatLongUTMconversion package which
# was borrowed from Dr. Kelly Thorp.
def get_lat_lon(exif_data):
    """Returns the latitude and longitude

    if available, from the provided exif_data (obtained
    through get_exif_data above)"""

    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

        # Added to compensate for any false GPS data from the image.
        # Some images (Canon specifically) were causing
        # errors becuase the program incorrectly identified them as
        # having GPS information.  This was causing the
        # program to abort when LatLongUTMconversion would be called with
        # lat/lon variables that didn't have numbers.
        # This required the if statement below to see if the lat/lon
        # variables were still set to their initialized values.
        if lat == None or lon == None:
            UTMrec = [0,0,0]
        else:
            UTMrec = LatLongUTMconversion.LLtoUTM(23, float(lat), float(lon))

    # return lat, lon
    return UTMrec


# Added to Will's code to ask for the file path to the top level image folder.
# The folder dialog box appears
# when the program first starts and sets the top folder for the application
# to start walking through.
def AskForFilepath():

    #   User selects a folder containing all the raw data files
    print "Select a folder containing all sensor files-"
    filepath = fd.askdirectory()

    return filepath


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


def exif_execution(top_folder):

    match_list = []
    match_folder = []

    # find all matches in the sub dirs
    for root, dirnames, filenames in os.walk(top_folder):
        for filename in fnmatch.filter(filenames, 'IMG_*.jpg'):
            match_list.append(os.path.join(root, filename))
            if root not in match_folder:
                match_folder.append(root)

    exif_files = []

    # Loop through available folders,
    # then create a csv containing metadata (the gps coords)
    # of the images within that folder
    for path in match_folder:

        exif_file = path + "\Exif_data.csv"
        print "Working in " + path

        exif_files.append(exif_file)
        files_in_folder = []

        # looks for files only in path
        for i in match_list:
            if (path in i) and (i not in files_in_folder):
                files_in_folder.append(i)

        # open new file in each dir
        with open(exif_file, "wb") as ef:
            writer = csv.writer(ef, delimiter=',')
            header = ["Image_Path",
                      "Dimensions",
                      "Size",
                      "Latitude",
                      "Longitude",
                      "UTM_X",
                      "UTM_Y",
                      "Make",
                      "Model",
                      "Date Time Original",
                      "ISO Speed",
                      "Exposure Bias",
                      "Aperture Value",
                      "Metering Mode",
                      "Focal Length",
                      "FStop",
                      "Exposure Time"]
            writer.writerow(header)

            # extract GPS from each image
            for file_ in files_in_folder:

                # enters the exif data of all jpgs into the database
                im = Image.open(file_)
                # Place all the exif data into the exif_data variable
                exif_data = get_exif_data(im)

                # Need to convert the lat long that the GPS reciever gives
                # us into something more meaningful to
                # our GIS programs like ArcGIS and QGIS
                # Call get_lat_lon procedure to do the UTM conversions for us
                try:
                    UTMrec = get_lat_lon(exif_data)
                except UnboundLocalError:
                    continue

                # Getting physical data from the operating system ##
                # How much hard drive space does this file consume.
                physical_size = os.path.getsize(file_)
                # Dividing the physical size by 1000 to display in Kilobytes
                display_phy_size = long(physical_size / 1000)
                # Adding the KB at the end so there is no doubt
                # what the number represents
                physical_size = str(display_phy_size) + "KB"

                # This was already done during the conversion but needed to
                # get the Latitude and Longitude again
                # since the variables are local to the conversion Def above.
                # Lazy programming, didn't have much
                # time to complete this portion.  This may be cleaned up later.
                # The if statement had to be changed in this portion of the
                # code because files that did not have
                # GPS info were registering as though they did.
                # This created an issue where no values were present
                # for the lat/long which was causing the file writing process
                # to raise an error.  The code in the
                # UTM conversion routine was also changed bacause images
                # without GPS information were trying to pass
                # values to the UTM conversion routine which was causing
                # the program to abort also.
                if UTMrec[1] != 0 or UTMrec[2] != 0:
                    gps_info = exif_data["GPSInfo"]
                    gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
                    gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
                    gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
                    gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

                    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                        lat = _convert_to_degress(gps_latitude)
                        if gps_latitude_ref != "N":
                            lat = 0 - lat

                        lon = _convert_to_degress(gps_longitude)
                        if gps_longitude_ref != "E":
                            lon = 0 - lon
                else:
                    lat = 0
                    lon = 0

                line = im.filename, \
                    im.size, \
                    physical_size, \
                    lat, \
                    lon, \
                    str(UTMrec[1]), \
                    str(UTMrec[2]), \
                    exif_data["Make"], \
                    exif_data["Model"], \
                    exif_data["DateTimeOriginal"], \
                    exif_data["ISOSpeedRatings"], \
                    exif_data["ExposureBiasValue"], \
                    exif_data["ApertureValue"], \
                    exif_data["MeteringMode"], \
                    exif_data["FocalLength"], \
                    exif_data["FNumber"], \
                    exif_data["ExposureTime"]

                print im.filename, \
                    lat, \
                    lon, \
                    str(UTMrec[1]), \
                    str(UTMrec[2])

                writer.writerow(line)

    print "Exif data extraction successful! "

    return exif_files


# Run PlantCV to find object in image
def find_object(image, rand_int):

    head, tail = os.path.split(image)
    print "Finding object in image " + tail + "..."

    # Read image
    img, path, filename = pcv.readimage(image)

    # Pipeline step
    device = rand_int

    debug = "print"  # or "plot"

    # Convert RGB to HSV and extract the Saturation channel
    # hue, saturation, value
    device, h = pcv.rgb2gray_hsv(img, 'h', device)

    # Threshold the Saturation image
    device, h_thresh = pcv.binary_threshold(h, 30, 255, 'light', device)

    device, h_mblur = pcv.median_blur(h_thresh, 5, device)
    device, h_cnt = pcv.median_blur(h_thresh, 5, device)

    # Fill small objects
    device, ab_fill = pcv.fill(h_mblur, h_mblur, 200, device)

    # Apply Mask (for vis images, mask_color=white)
    device, masked = pcv.apply_mask(img, h_mblur, 'white', device)

    # Identify objects
    device, id_objects,obj_hierarchy = pcv.find_objects(masked, h_mblur, device)

    # Define ROI
    device, roi1, roi_hierarchy = pcv.define_roi(masked, 'rectangle', device, None, 'default', False, 0, 0, 0, 0)

    # Decide which objects to keep
    device, roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img, 'partial', roi1, roi_hierarchy, id_objects, obj_hierarchy, device, debug)

    return


def delete_masks(rint):
    """ Delete the created masks of the image """

    os.remove(rint + "_obj_on_img.png")
    os.remove(rint + "_roi_mask.png")
    os.remove(rint + "_roi_objects.png")

    return


def find_images(top_folder):
    """ Find the images with matches and return their path with plot id"""

    match_list = []
    all_plots = []
    all_images = []

    for root, dirnames, filenames in os.walk(top_folder):
        for filename in fnmatch.filter(filenames, 'Plot_Match.csv'):
            match_list.append(os.path.join(root, filename))

    for f in match_list:
        with open(f, "rb") as pm:
            reader = list(csv.reader(pm, delimiter=","))

        for r in range(len(reader)):
            all_images.append(reader[r][0])
            all_plots.append(reader[r][1])

    return all_images, all_plots


def cull(vari, tgi, ngrdi, gli):
    """Find indices where values are not real. then remove them"""

    vari_mask = []
    tgi_mask = []
    ngrdi_mask = []
    gli_mask = []

    for i in range(len(vari)):

        if vari[i] < 0.:
            vari_mask.append(i)

        if tgi[i] < 0.:
            tgi_mask.append(i)

        if ngrdi[i] < 0.:
            ngrdi_mask.append(i)

        if gli[i] < 0.:
            gli_mask.append(i)

    vari_cull = np.delete(vari, vari_mask)
    tgi_cull = np.delete(tgi, tgi_mask)
    ngrdi_cull = np.delete(ngrdi, ngrdi_mask)
    gli_cull = np.delete(gli, gli_mask)

    return vari_cull, tgi_cull, ngrdi_cull, gli_cull


def rgb_counter(top_folder, image, plot_id, rint):
    """Find the pixel with plants and extract the band values

    This is where the core data extraction happens. The plant image and the
    masked plant image are compared, then wherever the mask shows there to
    be a plant, that pixel is harvested. The other pixels are not included.
    Then the VI are calculated but in the values of sums and counts of pixels
    """

    mask = r"C:\Users\William.Yingling\Scripts\\" + rint + "_obj_on_img.png"

    # Read image bands. then smoosh it to a 1D array
    image_data = sp.imread(image).astype(np.float64)
    image_slice_red = image_data[:, :, 0].flatten()
    image_slice_green = image_data[:, :, 1].flatten()
    image_slice_blue = image_data[:, :, 2].flatten()

    # Read mask image and take green band from it.
    # Where the mask is max val 255 means thats the plant object
    mask_data = sp.imread(mask).astype(np.int)
    mask_slice_green = mask_data[:, :, 1].flatten()

    # If mask is not max val, then pixel represents not plant matter
    # so give it a fake negative val so we can delete it in the next step
    image_slice_red[mask_slice_green != 255] = -1
    image_slice_green[mask_slice_green != 255] = -1
    image_slice_blue[mask_slice_green != 255] = -1

    # Find the indices where the negative value is
    del_indices = np.argwhere(image_slice_green == -1)

    # Create arrays where only plant matter is included
    red_arr = np.delete(image_slice_red, del_indices)
    green_arr = np.delete(image_slice_green, del_indices)
    blue_arr = np.delete(image_slice_blue, del_indices)

    # Filter the arrays to make sure they are within 1 std of themselves
    try:
        red, green, blue = rgb_filter(red_arr, green_arr, blue_arr)
    except IndexError:
        print "No masked Pixels!"
        return

    # Calculate Vegetation indices
    vari_raw = calculate_vari(red, green, blue)
    tgi_raw = calculate_tgi(red, green, blue)
    ngrdi_raw = calculate_ngrdi(red, green, blue)
    gli_raw = calculate_gli(red, green, blue)

    # If VI are a negative number, remove
    vari, tgi, ngrdi, gli = cull(vari_raw, tgi_raw, ngrdi_raw, gli_raw)

    # sum the VIs
    vari_sum = np.nansum(vari)
    tgi_sum = np.nansum(tgi)
    ngrdi_sum = np.nansum(ngrdi)
    gli_sum = np.nansum(gli)

    ndvi_file = top_folder + "\VI_Data.csv"

    # Write vals to file
    # Writes sum of the VIs and the number of vals. Avgs will be calcd later
    with open(ndvi_file, "ab") as nf:
        writer = csv.writer(nf, delimiter=',')

        writer.writerow([image, plot_id,
                         vari_sum, len(vari),
                         tgi_sum, len(tgi),
                         ngrdi_sum, len(ngrdi),
                         gli_sum, len(gli)])

    return


def filter_images(top_folder, image, rint, green_tolerance):

    #print "Looking for dirt..."

    mask = r"C:\Users\William.Yingling\Scripts\\" + rint + "_obj_on_img.png"

    image_data = sp.imread(image).astype(np.float64)

    image_slice_red = image_data[:, :, 0].flatten()
    image_slice_green = image_data[:, :, 1].flatten()
    image_slice_blue = image_data[:, :, 2].flatten()

    mask_data = sp.imread(mask).astype(np.int)
    #mask_slice_red = mask_data[:, :, 0].flatten()
    mask_slice_green = mask_data[:, :, 1].flatten()
    #mask_slice_blue = mask_data[:, :, 2].flatten()

    gt_data = sp.imread(mask).astype(np.float64)
    gt_slice = gt_data[:, :, 1]
    band_size = float(gt_slice.size)
    green_count = float(np.count_nonzero(gt_slice == 255))
    ratio_green_pix = float(green_count) / float(band_size)

    image_slice_red[mask_slice_green != 255] = -1
    image_slice_green[mask_slice_green != 255] = -1
    image_slice_blue[mask_slice_green != 255] = -1

    del_indices = np.argwhere(image_slice_green == -1)

    red_arr = np.delete(image_slice_red, del_indices)
    green_arr = np.delete(image_slice_green, del_indices)
    blue_arr = np.delete(image_slice_blue, del_indices)

    # Pixel Check. Find the most average pixels of the group
    try:
        red, green, blue = rgb_filter(red_arr, green_arr, blue_arr)
    except IndexError:
        print "No masked Pixels!"
        return

    vari_raw = calculate_vari(red, green, blue)
    tgi_raw = calculate_tgi(red, green, blue)
    ngrdi_raw = calculate_ngrdi(red, green, blue)
    gli_raw = calculate_gli(red, green, blue)

    vari, tgi, ngrdi, gli = cull(vari_raw, tgi_raw, ngrdi_raw, gli_raw)

    vari_sum = np.nansum(vari)
    tgi_sum = np.nansum(tgi)
    ngrdi_sum = np.nansum(ngrdi)
    gli_sum = np.nansum(gli)

    ndvi_file = top_folder + "\GreenTolerance.csv"

    with open(ndvi_file, "ab") as nf:
        writer = csv.writer(nf, delimiter=',')

        writer.writerow([image, ratio_green_pix,
                         vari_sum, len(vari),
                         tgi_sum, len(tgi),
                         ngrdi_sum, len(ngrdi),
                         gli_sum, len(gli)])

    # We found dirt
    if ratio_green_pix < green_tolerance:
        return None

    return image


def create_vi_file(top_folder, file_name, image_list, plot_list, gt_file, dirt):


    vi_file = top_folder + file_name

    with open(gt_file, "rb") as gt:
        reader = list(csv.reader(gt, delimiter=","))

    vi_rows = []

    for r, row in enumerate(reader):

        if row[0] in dirt:
            continue

        for i, il in enumerate(image_list):

            if il == row[0]:
                # switch the green index for plot assignment
                row[1] = plot_list[i]

        vi_rows.append(row)

    with open(vi_file, "wb") as nf:
        writer = csv.writer(nf, delimiter=',')

        header = ["Image_Path", "Plot",
                  "VARI", "VARI_Count",
                  "TGI", "TGI_Count",
                  "NDGRDI", "NGRDI_Count",
                  "GLI", "GLI_Count"]

        writer.writerow(header)

        for vir in vi_rows:

            writer.writerow(vir)

    return


def create_gt_file(vi_file):

    with open(vi_file, "wb") as nf:
        writer = csv.writer(nf, delimiter=',')

    return


# Added to Will's code to ask for the file path to the top level image folder.
# The folder dialog box appears
# when the program first starts and sets the top folder for the application to
# start walking through.
def ask_for_top_folder():

    #   User selects a folder containing all the raw data files
    print "Select a folder containing all sensor files-"
    filepath = fd.askdirectory()

    return filepath


def ask_for_box_data():

    #   User selects a folder containing all the raw data files
    print "Select a folder containing all sensor files-"
    filepath = fd.askopenfile()

    return filepath


def read_csv(file_path):
    """ Read the CSV File """

    with open(file_path, "rb") as fp:
        reader = list(csv.reader(fp, delimiter=","))
        reader.pop(0)

    return reader


def condense(contents, seed_ids):
    """ Take the contents and then avg the plots' values """

    condensed_file = []

    for plot in seed_ids:

        tot_vals = []

        for row in contents:

            # Hard Fault Error Catch
            if len(row) != 10:
                continue

            if row[1] == plot:
                tot_vals.append(row)

        if len(tot_vals) == 0:
            calcd_vals = [np.nan, np.nan, np.nan, np.nan]
        else:
            calcd_vals = avg_vals(tot_vals)

        calcd_row = [plot] + calcd_vals

        condensed_file.append(calcd_row)

    return condensed_file


def make_csv(file_path, condensed):
    """ Put the info into a csv """

    with open(file_path, "wb") as f:
        writer = csv.writer(f, delimiter=",")

        header = ["Plot", "VARI", "TGI", "NDGRI", "GLI"]
        writer.writerow(header)

        for row in condensed:

            writer.writerow(row)

    return


def avg_vals(tot_vals):
    """ Average the the values in the plot """

    vals_t = np.array(tot_vals)
    vals_transposed = np.transpose(vals_t)
    vals = np.array(vals_transposed[2:]).astype(np.float64)

    # if there are bad vals then give a value of nan
    vals[0][vals[0] == np.inf] = np.nan
    vals[1][vals[0] == np.inf] = np.nan
    vals[2][vals[2] == np.inf] = np.nan
    vals[3][vals[2] == np.inf] = np.nan
    vals[4][vals[4] == np.inf] = np.nan
    vals[5][vals[4] == np.inf] = np.nan
    vals[6][vals[6] == np.inf] = np.nan
    vals[7][vals[6] == np.inf] = np.nan

    vari = np.nansum(vals[0])
    v_counts = np.nansum(vals[1])

    tgi = np.nansum(vals[2])
    t_counts = np.nansum(vals[3])

    ndgri = np.nansum(vals[4])
    n_counts = np.nansum(vals[5])

    gli = np.nansum(vals[6])
    g_counts = np.nansum(vals[7])

    vari_avg = vari / v_counts
    tgi_avg = tgi / t_counts
    ndgri_avg = ndgri / n_counts
    gli_avg = gli / g_counts

    return [vari_avg, tgi_avg, ndgri_avg, gli_avg]


def condense_vi(top_folder, seed_id):
    """Read VI then consolodate it to per plot"""

    file_path = top_folder + "\VI_Data.csv"
    condensed_file = top_folder + "\VI_Data_Condensed.csv"

    contents = read_csv(file_path)
    condensed = condense(contents, seed_id)
    make_csv(condensed_file, condensed)

    return


def write_gopp(top_folder, gopp):
    """ Put the info into a csv """

    file_path = top_folder + "\Gopp.csv"

    with open(file_path, "wb") as f:
        writer = csv.writer(f, delimiter=",")

        for row in gopp:

            writer.writerow(row)

    return


def chunks(l):
    """ Yield successive n-sized chunks from l. """

    seg = len(l) / 4

    for i in xrange(0, len(l), seg):
        yield l[i:i + seg]


def dirt_finder_multiprocessing(arg_inputs):
    """ Multiprocessing to find ratio of plant to dirt. Return list of dirt """

    top_folder = arg_inputs[0]
    img_paths = arg_inputs[1]
    rand_int = int(arg_inputs[2])
    green_tolerance = arg_inputs[3]

    rint = str(rand_int + 9)

    dirt = []

    for i, image in enumerate(img_paths):

        find_object(image, rand_int)
        im_dirt = filter_images(top_folder, image, rint, green_tolerance)
        delete_masks(rint)

        if im_dirt is None:
            dirt.append(image)

    return dirt

"""
def rgb_finder_multiprocessing(arg_inputs):
    " Multiprocessing to find rgb info in each image "

    top_folder = arg_inputs[0]
    img_list = arg_inputs[1]
    plot_list = arg_inputs[2]
    rand_int = int(arg_inputs[3])

    rint = str(rand_int + 9)

    for i, image in enumerate(img_list):

        find_object(image, rand_int)
        rgb_counter(top_folder, image, plot_list[i], rint)
        delete_masks(rint)

    return
"""

def reanalyze(top_folder, img_paths, ra_images,
              green_tolerance, dirt, gt_file):
    """ Reanalyze gopp. Recursive funct to reduce group size """

    redo = False

    dirt_tail = []
    image_reanalyze = []

    for i in dirt:
        head, tail = os.path.split(i)
        dirt_tail.append(tail)

    print "reanalyze green_tolerance ", green_tolerance, ra_images[0], \
          ra_images[-1], dirt_tail

    with open(gt_file, "rb") as gt:
        reader = list(csv.reader(gt, delimiter=","))

    start_index = None
    end_index = None

    for r, row in enumerate(reader):

        if row[0] == ra_images[0]:
            start_index = r
        if row[0] == ra_images[-1]:
            end_index = r

    if start_index is None:
        start_index = 0
    if end_index is None:
        end_index = len(reader)-1

    for p, prow in enumerate(reader):
        if p >= start_index and p <= end_index:
            if float(prow[1]) <= green_tolerance and prow[0] not in dirt:
                dirt.append(prow[0])

    dirt.sort()

    if len(dirt) > 0:
        for d in range(len(dirt) - 1):

            # boolean variables
            dd = dirt[d] in ra_images
            ddone = dirt[d+1] in ra_images

            # redefine starting and ending images
            first_im = dirt[d]
            last_im = dirt[d+1]

            # if bounds are not avaiable, look for img one before or one after
            if dd is False:
                first_im = ra_images[0]
            if ddone is False:
                last_im = ra_images[-1]

            if dirt[d] in ra_images or dirt[d+1] in ra_images:

                print first_im,img_paths.index(first_im), last_im, img_paths.index(last_im)
                if (img_paths.index(last_im) - img_paths.index(first_im) > 16):

                    print "found a match!", first_im, last_im
                    print img_paths[img_paths.index(first_im):img_paths.index(last_im)]

                    # redefine
                    image_reanalyze += img_paths[img_paths.index(first_im):img_paths.index(last_im)]
                    redo = True

        if len(image_reanalyze) > 0:
            ra_images = image_reanalyze

    last_dirt_im = None

    # check dirt in ra_images
    for i in ra_images:
        for j in dirt:
            if i == j:
                last_dirt_im = j

    if (len(dirt) == 0 or redo is True or
       (last_dirt_im is None and len(ra_images) > 16)) \
       and green_tolerance < .6:
        print "redo!! ", redo #, dirt

        green_tolerance += 0.1
        reanalyze(top_folder, img_paths, ra_images,
                  green_tolerance, dirt, gt_file)

    return dirt


def gopp_filter(top_folder, img_utm, gopp, green_tolerance,
                dirt, image_ranges, gt_file):
    """ Filter to  check if group is reasonable and expected """

    new_gopp = []

    # loop through each group in gopp list
    for rang in gopp:

        new_range = []

        for group in rang:

            min_lat = None
            max_lat = None

            min_long = None
            max_long = None

            # loop through images in the group
            for img in group:

                current_lat = img_utm[img][0]
                current_long = img_utm[img][1]

                # find min and max values of images in group
                if current_lat > max_lat or max_lat is None:
                    max_lat = current_lat
                if current_lat < min_lat or min_lat is None:
                    min_lat = current_lat
                if current_long > max_long or max_long is None:
                    max_long = current_long
                if current_long < min_long or min_long is None:
                    min_long = current_long

                plot_length = abs(max_lat - min_lat)
                plot_width = abs(max_long - min_long)

            # if group is too populated or too big, then reanalyze group.
            if len(group) > 16 or plot_length > 8. or plot_width > 3.:

                gt = green_tolerance + 0.05

                new_dirt = reanalyze(top_folder, group, group, gt, dirt, gt_file)

                new_group = list(group_plots_ra(group, new_dirt, image_ranges))

                dirt = new_dirt

                for ng in new_group:

                    new_range.append(ng)

                continue

            new_range.append(group)

        new_gopp.append(new_range)

    for i in new_gopp:
        print "Images in range (gopp_filter) ", len(i)

    return tuple(new_gopp), dirt


def open_planning_file(planning_file):
    """ open planning file and extract ranges and columns """

    with open(planning_file, "rb") as pf:
        reader = list(csv.reader(pf, delimiter=","))

    ranges = []
    columns = []

    for j in range(len(reader[0])):
        current_range = []
        for k in range(len(reader)):
            if reader[k][j] != "empty":
                current_range.append(reader[k][j])
        if len(current_range) != 0:
            current_range.reverse()
            ranges.append(current_range)

    for col in range(len(ranges[0])):
        current_column = []
        for row in range(len(ranges)):
            current_column.append(ranges[row][col])
        columns.append(current_column)

    return ranges, columns


def closest_plot(seed_box, plot_list, lat, longi):
    """ Find closest plot to given lat and long """

    diff_match = None

    for pl in plot_list:

        sb_coords = seed_box[pl]

        diff = diff_calc(lat, longi, sb_coords)

        if diff < diff_match or diff_match is None:
            diff_match = diff
            plot_match = pl

    return plot_match


def border_reassignment(seed_box, ranges, columns):
    """ Assign unique names to the groups of border plants.

    Can easily break!
    """

    r_len = len(ranges)
    c_len = len(columns)

    br_keys = []
    for k in seed_box.keys():
        if "Br" in k:
            br_keys.append(k)

    for c in range(1, c_len-1):
        for i in range(1, len(columns[c])-1):

            if "Br" in columns[c][i]:
                continue

            lat = seed_box[columns[c][i]][0]
            longi = seed_box[columns[c][i]][1]

            plot_match = closest_plot(seed_box, br_keys, lat, longi)

            if columns[c][i+1] == "Br":
                columns[c][i+1] = plot_match
                br_keys.remove(plot_match)
            elif columns[c][i-1] == "Br":
                columns[c][i-1] = plot_match
                br_keys.remove(plot_match)

    lat = seed_box[columns[1][0]][0]
    longi = seed_box[columns[1][0]][1]

    plot_match = closest_plot(seed_box, br_keys, lat, longi)

    columns[0][0] = plot_match
    br_keys.remove(plot_match)

    for i in range(1, len(columns[0])):

        lat = seed_box[columns[0][i-1]][0]
        longi = seed_box[columns[0][i-1]][1]

        plot_match = closest_plot(seed_box, br_keys, lat, longi)

        columns[0][i] = plot_match
        br_keys.remove(plot_match)

    lat = seed_box[columns[-2][0]][0]
    longi = seed_box[columns[-2][0]][1]

    plot_match = closest_plot(seed_box, br_keys, lat, longi)

    columns[-1][0] = plot_match
    br_keys.remove(plot_match)

    for i in range(1, len(columns[-1])):

        lat = seed_box[columns[-1][i-1]][0]
        longi = seed_box[columns[-1][i-1]][1]

        plot_match = closest_plot(seed_box, br_keys, lat, longi)

        columns[-1][i] = plot_match
        br_keys.remove(plot_match)

    for i in range(len(ranges)):
        for j in range(len(ranges[i])):
            if ranges[i][j] == "Br":
                ranges[i][j] = columns[j][i]

    return ranges, columns


def range_check(avg_coords, seed_box, ranges):
    """ Decide which range from planning file matches with image range """

    calcd_range = []
    calcd_pir = []
    calcd_adjusted_plots = []
    calcd_dist = []

    print "Range_Check"

    for avg_range in avg_coords:

        best_fit = None
        range_match = None
        br_keys = []

        # put br keys into a new list since they need special treatment
        for k in seed_box.keys():
            if "Br" in k:
                br_keys.append(k)

        # loop through ranges in gopp list
        for i in range(len(ranges)):

            plots_in_range = []
            coord_match = 0.

            # loop through plots
            for a in range(len(avg_range)):

                lat = avg_range[a][0]
                longi = avg_range[a][1]

                diff_match = None

                # find closest plot
                for j in range(len(ranges[i])):

                    sb_coords = seed_box[ranges[i][j]]
                    diff = diff_calc(lat, longi, sb_coords)

                    if diff_match is None or diff < diff_match:
                        diff_match = diff
                        plot_match = ranges[i][j]

                # put plot match into range list. add up dist away from range
                plots_in_range.append(plot_match)
                coord_match += diff_match

            # continually update the best fitting range and include assoc data
            if best_fit is None or coord_match < best_fit:

                best_fit = coord_match
                range_match = ranges[i]
                good_pir = plots_in_range

        adjusted_plots = []
        dist = []

        # loop through plots again for the plot readjustment
        for c in range(len(avg_range)):

            lat = avg_range[c][0]
            longi = avg_range[c][1]

            diff_match = None

            # loop through the specified good range to find plot match
            for p in range_match:

                sb_coords = seed_box[p]
                #diff = diff_calc_utm_x(lat, longi, sb_coords)
                diff = diff_calc(lat, longi, sb_coords)

                if diff_match is None or diff < diff_match:
                    diff_match = diff
                    plot_match = p

            adjusted_plots.append(plot_match)
            dist.append(diff_match)

        print "Best range match", range_match, best_fit

        # collect all of the information
        calcd_range.append(range_match)
        calcd_dist.append(dist)
        calcd_pir.append(good_pir)
        calcd_adjusted_plots.append(adjusted_plots)

    return calcd_pir, calcd_dist


def find_ranges(img_path, dirt, gt_file):
    """ Find where theres large gaps of dirt and define in between as range """

    image_ranges = []
    local_group = []

    dirt_counter = 0.
    range_tolerance = 8

    with open(gt_file, "rb") as gtf:
        reader = list(csv.reader(gtf, delimiter=","))

    for ip in range(len(img_path)):

        gt = None
        gt_counts = None

        # this is to help catch bright shadows
        for row in reader:
            if row[0] == img_path[ip]:
                gt = float(row[1])
                gt_counts = int(row[5])

        if img_path[ip] in dirt:
            dirt_counter += 1
        # bright shadows will have high green tolerance and low viable data
        elif gt > 0.8 and gt_counts < 100000:
            dirt.append(img_path[ip])
            dirt_counter += 1

        else:  # img_path[ip] not in dirt:
            dirt_counter = 0.

        local_group.append(img_path[ip])

        if dirt_counter == range_tolerance or \
           (len(local_group) > 0 and ip == len(img_path)-1):

            image_ranges.append(local_group)
            local_group = []

    return image_ranges, dirt


def write_range_match(top_folder, file_name, calcd_pir, calcd_dist):
    """ Write a file showing the total distance the plots deviate from range"""

    vi_file = top_folder + file_name

    with open(vi_file, "wb") as nf:
        writer = csv.writer(nf, delimiter=',')

        header = ["Dist", "Good Range"]

        writer.writerow(header)

        for i in range(len(calcd_pir)):
            row = [sum(calcd_dist[i])] + calcd_pir[i]

            writer.writerow(row)

    return


def order_gt(top_folder, gt_file):
    """ Alphabatize the paths, since multiprocessing shuffled everything """

    with open(gt_file, "rb") as gt:
        reader = list(csv.reader(gt, delimiter=","))

    image_data = []

    # remove faults, if there are any
    for r in reader:
        if len(r) != 10:
            continue

        image_data.append(r)

    # sorting function. sort list by first item in the elements (list)
    image_data.sort(key=lambda x: x[0])

    gt_file_new = top_folder + "\New_GT.csv"

    with open(gt_file_new, "wb") as gfw:
        writer = csv.writer(gfw, delimiter=",")

        for i in image_data:

            writer.writerow(i)

    return gt_file_new


# ########################################################################### #
# --------------------------------------------------------------------------- #
#                                    Main Pipeline                            #
# --------------------------------------------------------------------------- #
# ########################################################################### #
def main():

    start_time = time.time()

    #top_folder = ask_for_top_folder()
    #box_data = ask_for_box_data()

    top_folder = r"E:\Tractor_Images\F120\Run13\\"
    box_data = r"E:\Tractor_Images\F120\All_generated_boxes.csv"
    planning_file = r"E:\Tractor_Images\F120\F120_Planning_2016_Corrected.csv"

    # read in seed_box with corresponding id
    seed_box, seed_id = read_boxes(box_data)

    # create exif data from images
    exif_files = exif_execution(top_folder)

    # extract exif data from all img files
    img_utm = read_exif(exif_files)

    # find all img paths in dict
    img_path = img_utm.keys()
    img_path.sort()

    # initialize lists
    dirt = []
    arg_inputs_one = []
    arg_inputs_two = []
    groups_of_plot_paths = []

    # for multiprocessing. split img_path list into segments
    img_path_split = list(chunks(img_path))

    # device number for the PlantCV function
    random.seed(101)

    # tolerance level for initial percentage of plant matter in image
    green_tolerance = 0.1

    print "green tolerance ", green_tolerance

    gt_file = top_folder + "\GreenTolerance.csv"

    create_gt_file(gt_file)

    # create list with all args for multiprocessing
    for ips in img_path_split:
        arg_inputs_one.append([top_folder, ips,
                               random.randint(1, 100000), green_tolerance])

    # Launch multiprocessing
    p = Pool(5)
    bad_images = p.map(dirt_finder_multiprocessing, arg_inputs_one)

    # group together images with dirt into a neat list
    for bi in bad_images:
        for b in bi:
            dirt.append(b)

    dirt.sort()

    gt_file = order_gt(top_folder, gt_file)

    image_ranges, dirt = find_ranges(img_path, dirt, gt_file)

    # group plots together based off of dirt
    groups_of_plot_paths = group_plots(img_path, dirt, image_ranges)

    #print "groups of plot paths ", groups_of_plot_paths

    # examine and reanalyze gopp to make sure plots are grouped correctly
    groups_of_plot_paths, dirt = gopp_filter(top_folder, img_utm,
                                             groups_of_plot_paths,
                                             green_tolerance, dirt,
                                             image_ranges, gt_file)

    # write a gopp file for dev inspection. Completely optional.
    write_gopp(top_folder, groups_of_plot_paths)

    # find avg coords of each group of plots
    avg_coords = avg_plots(groups_of_plot_paths, img_utm)

    # Open the planning file and extract the rows and columns
    ranges_br, columns_br = open_planning_file(planning_file)

    ranges, columns = border_reassignment(seed_box, ranges_br, columns_br)

    calcd_pir, calcd_dist = range_check(avg_coords, seed_box, ranges)

    # write a range_match file for dev inspection. Completely optional.
    write_range_match(top_folder, "\Range_Match.csv", calcd_pir, calcd_dist)

    # assign a plot name to group of plots
    image_list = assign_plot(top_folder, groups_of_plot_paths,
                             calcd_pir, calcd_dist)

    # gather list of images available
    image_list, plot_list = find_images(top_folder)

    # create a file for the vegetation indices data to be stored in
    create_vi_file(top_folder, "\VI_Data.csv", image_list, plot_list, gt_file, dirt)

    # take vi data of images and consolodate it to each plot
    condense_vi(top_folder, seed_id)

    tot_time = str(round(time.time() - start_time, 2))

    print "Program finished running. " + tot_time + " seconds"


if __name__ == '__main__':
    main()

# Will Yingling
# Biological Science Technician, USDA
# August 2017
