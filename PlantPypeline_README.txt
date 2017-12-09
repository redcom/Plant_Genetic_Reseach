This file is associated with the "PlantPypipeline.py" executable/file.

This script takes three arguments:
1) Top Folder where the script will operate
1) All_boxes file from the original project
2) Planning file. for plot asignment

The Output:
There will be a handful of files that will be helpful.
Gopp.csv
GreenTolerance.csv
New_GT.csv
Plot_Match.csv
Range Match.csv
VI_Data.csv
VI_Data_Condensed.csv

To Execute:
$ python PlantPypeline.py


Primary Function:
The primary function of this script is to extract the RGB data from tractor
images, assign the image location to a known plot,
and convert the RGB ratios into Vegetation Indices (VARI, TGI, NGRDI, GLI).


The Process:
The script will extract the GPS data from each image and
write to a file, exif_data.csv.
The GPS coords are initially in Lat Long form and are converted to UTM
further down the pipeline.

Next, the all_boxes file is read in. The information includes the defining
boundary points of each unique plot and the plot's corresponding name. These
coords are also put into UTM from Lat Long.
*Since the Br plants need a unique name, the script combines the "Br" with
the unique id in the file to compose a new unique name*
The all_boxes coords are averaged into one point in the x and y directions.
This conversion will be part of the image assignment later in the script.

Also read in is the planning file. This is to give the concrete formation of
the plots in relation to one another and also to help sift out the
images in a range. Each range of plots are grouped into lists.

Next, the list of all available images to be analyzed are split into a small
group of lists for multiprocessing. The lists are given a handful of parameters
and then multiprocessing is launched for analysis.

The analysis includes plant finding and mask creation, calculation, and
paring of the bad data.
1) Plant Finding. Utilizes plant-finding module PlantCV. This can take a bit of
knob turning to find the exact area of the plant. The module is generally
meant for greenhouse conditions but has been modified for tractor images.
This step will temporarily produce a masked image (actually 3 masks,
two are byproducts) of the original image where the plant matter is masked
a bright green. If an image does not meet the green tolerance criteria,
it is assumed to be dirt then placed in an according list for later.
2) Calculation. This step compares the original image to the masked image.
Numpy is used for this. The images are converted to flat arrays so image size
and shape wont have effects on matrice analysis. The masked array is looked at
to find where the plant matter exists (where green pixel is equal to max value
of 255). From there, we take the data from the original image array at the
specified indices of the masked array where the script thinks the plant matter
to be. The remaining of the data/dirt pixels are removed. The good values are
then run through a checker to find most average pixels of the group and then
extracts those. This means that to be selected, the values of each RGB band
must all fall within their respective averages to be considered satisfactory.
From here, the RGB values used to calculate the VIs.
3) Paring. The vegetation indices values are passed through a culling function
to remove the unsatisfactory VI values (from -1 to 0).

After these three steps, the VIs are then summed up and number of values
are tallied. This happens so they can be averaged further down the line for
all images assigned in a plot. Additionally a preliminary green ratio
calculation is made (masked pixels vs total pixels). The image path, green
ratio, and VARI tally, VARI sum, TGI tally, TGI sum, NGRDI tally, NGRDI sum,
GLI tally, and GLI sum are written to the the file "GreenTolerance.csv".

After the analysis steps, the GreenTolerance file is reordered because
multiprocessing has scrambled everything and we need the file to be in order.
This reordered file is named "New_GT.csv"

Now the scripts moves into the plot assignment portion.
Range Grouping. (Sequential images of dirt exceeds ~8)
The script looks at where the dirt is located in the relative
line up of image paths to decide how to group the images into specific ranges.
*There is an assumption here that the
tractor is not going to jump around from any plot to any plot but rather
move linearly across the field and so the images can therefore be constrained
to this path*.
Further segmentation is sometimes needed because sometimes
reflective shadows can throw off the grouping so there is a catch built in
for these shadows (they generally have terrible looking data and high green
ratios) so these images will be appended to the dirt list. The images in
between long sequences of dirt are then grouped as ranges.

Next, will be plot assignment of the images.
Plot Grouping (Sequential images of dirt between 0-8)
In the preliminary calculation for green tolerance
the images may or may not be grouped correctly. Often, the initial tolerance
was too low and the space in between plots was not registered as dirt so
images from neighboring plots can be grouped together. If this is true, there
are two ways the scripts may identify the grouping as incorrect: the image
coordinates are too far apart to be real or the number of images in a group is
greater than a determined threshold. The script will then pass into a recursive
function that looks through the images in the group and steadily increases
the green tolerance in hopes of finding dirt. When found, the dirt list will be
appended and the faulty group will be split into according sections until the
groupings meet the two aforementioned criteria.

Next, the images will be assigned a plot within the best fit range available.
So far, the images have been grouped together and then those are grouped into
ranges. The ranges are then compared to all of the ranges from the planning
file. Whichever range from the planning file is closest to the range from the
tractor will be the group of plots that will be available to be assigned to the
tractor images. The all_boxes plots have had a average coordinate calculated in
the X and Y directions. Similarly, the groups of images have had all of their
coordinates averaged over the entire group. From here, the coordinates from the
groups of images are compared to all available plot coordinates in that range.
The closest matching plot will be assigned to the entire group of images.
For the grouped plots in a specified range, the matched range and summed
distance of how far away the grouped plots are from their corresponding
assigned plot are written to "Range_Match.csv"
The image_paths, assigned plots, and distance away from plots
will be written to "Plot_Match.csv"

After assignment, the green tolerance from the "New_GT.csv" file will be
replaced with the assigned plot. And a new file will be written to
called "VI_Data.csv" with the new modified information.

Finally, "VI_Data.csv" will be read in and consolidated. Here is where the
plots will amalgamate all of their data from the individual images. Since
each image has the tally of viable pixels and the sum of the VI, each value
will be combined and when all images in the plot have been found the VIs
will be averaged. The plots and their associated averaged VIs are then written
to the final file titled "VI_Data_Condensed.csv"


# Will Yingling
# USDA Biological Science Technician
# October 2017



