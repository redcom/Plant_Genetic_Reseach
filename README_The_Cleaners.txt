*******************************************************************************
   This area is provided to assist the user on how to execute The_Cleaners
*******************************************************************************
Scroll down for more...

This software is to perform cleaning and analysis on the data.
The files that can be operated on are:
    CC_plots.csv
    IRT_forward_plots.csv
    IRT_nadir_plots.csv
    Honey_plots.csv
    Pep_plots.csv


GUI EXPLANATION:
The first entry box is for the directory in which the script is to operate in.
It can house a singular run or multiple runs.
The requirement is for "_Run##_" to appear anywhere within the path name
of where the sensor files are housed.
For example: "E:\htp\F120\_QC1 Output\2017_01_04_F120_Run01_DOY004"

In the next row, an option for "Stressors" refers to the first letter character
    in the plot name.
    For example, in the plot "W325N", you would enter "W".
    It is acceptable to have more than one stressor. When listing the stressors
    be sure not to include any spaces between characters.
    For example "W,D"
The last option in the same row is for the different species of plants.
    It is also acceptable to have more than one species.
    For example, for plot "W325N", the entry would be "N"
    Or if multiple, "N,J,C"

The next segment is to toggle which sensor to run, your 4 choices are:
    Crop Circle (Toggle CC_plot), Infrared Temperature (Toggle IRT_plot),
    Honeywell (Toggle Honey_plot), and Pepperl (Toggle Pep_plot)

    Simply click the gray bar to toggle which sensor you'd like to analyze.
    When you've clicked it, it should highlight green to let you know that
    analysis for that sensor will be executed.
    Note: The files must exist and have the same name as the files listed above

Within each section is the option to:
    -Define "Range". Here you may enter any two numbers that you'd like to
        establish as the range. The form is "0,1" without spaces.
        Note: The range given here defines the range of the Y-axis on the plots
        -- Don't Define Range.  A check box in the same row to let the script
           know you would not like to define any range
    -Plot Data. An option to create boxplots, per plot, of the sensor data.
        Note: Selecting this will also increase the amount of time
        the script takes to run. (Approx +1 min per species with 350 plots)
        -- If Toggle Range SD is selected, sensors with a mean outside of 1 SD
           of the plot mean will not show up because they have been thrown out.
           Also, a red dashed line and pink line will be drawn representing
           +/- 1 standard deviation and the mean, respectively.
    -Toggle Range SD. Refering to an analysis of taking the Standard Deviation
          of a plot's sensors, finding the mean, taking a range defined as the
          mean +\- 1 Standard Deviation, then taking the mean of the points
          found within that range and calculating their standard deviation.
          If the mean value of each sesnor is outside 1 standard deviation of
          the new mean, then that sensor will be removed.
    -Remove Zeros. This will remove any values that are exactly zero
    -Reanalyze Stat. This option is for if you have already run the script
         and have visually identified bad sensors that need to be removed. To
         effectively remove the sensors, there will be a file within
         /Cleaned_Data/ called (Sensor)_preened.csv, open it and enter the
         sensors into the file, abiding by the format laid out.


DATA PRODUCTS:
In this script, many files get created.
In the directory where (Sensor)_plots.csv are housed, the created objects are

    (Sensor)_plots_cleaned.csv
    \Cleaned_Data\

    The "_cleaned" data reflects the Zeros Toggle and Range Toggle from the GUI
    - The cleaned data will have the zeros replaced with nan values and
      the values outside of the specified range will also be given nan
    - This is the data that gets analyzed later on down the road.

    In \Cleaned_Data\
    - Stats_(Trait).csv gets made. These small files are for the Excel Compiler
      They contain the average value of the plot.
    - (Sensor)_(Trait).pdf is an optional file that gets made. These are the
      pdf images of the boxplots when the data was analyzed. They can be
      singluar or multiple pages long, depending on amount of species given.
      The subplots are given a square-like matrix and so to help conform
      to that shape, there are a few empty plots to fill the space (These are
      typical and do not indicate that an error has occured).
    - (Sensor)_preened.csv This is a file that gets made to help the script
      identify what sensor(s) to cull out of the analysis. The file will always
      be made, but will only include sensors when "Toggle Plot SD" is executed.
      This is where you might type in sensors you deem to be bad and then you
      would rerun the script and toggle "Reanalyze Stats" in order to filter
      out those sensors too.
    - Parameters_Used.txt Gives the user a history and time of the parameters
      executed last for the purpose of keeping records and verifying the
      correct paramters were used.


COMPILING:
After the script has finished running, execute the Excel_Compiler.py script
    to combine all of the stat data. Like so

    Open Command Prompt:
    $ cd to/the/script
    $ python Excel_Compiler.exe

    When executed the script will wait for you to then enter in a file path
    $ Enter top folder:

    Type in the file path, then hit Enter, which might look like
    $ Enter top folder: E:\htp\F120\_QC1 Output

This will produce a .xlsx file named "Complete_Stats" where each trait is
    chronologically ordered and each trait is on a separate sheet


TROUBLESHOOTING:
This section is to help the user get to the bottom of the problems
they may be experiencing. The error labels are loose paraphrasings.

"Table already exists"
    Go into the \Cleaned_Data\ folder and remove "Temp_enchilda.db"
    If the computer says the file is locked and can't close, then close
    Commpand Prompt and try to delete it again. Then rerun the script

"(Sensor)_plots.csv has no attribute 'PLOT'"
    This means the plot ID column in the .csv file does not exist
    or is misspelled.
    Go into the file and investigate. If there is a misspelling, change the
    column header to 'PLOT'.

The script isn't analyzing the data, but completes running safely:
    Double check that you are giving the correct Stressors and Species in
    the GUI. In this problem, the "Beginning Stat Analysis" section
    will breeze through in a matter of seconds, rather than minutes. The
    to see this effect, the script prints out a time after the analysis
    that looks like "--- #.# seconds --- "
    Additionally, if no Trait or Plot ID are printed to the screen during
    "Beginning Stat Analysis", then script is not finding the plots.
    The problem could also be that the plot ids are
    not of the format "(A-Z)###(A-Z)" aka "W325N". This issue is a fatal flaw
    and the remedy is to change the name of each id to match the format the
    script is expecting.



To alternatively execute this file in Command Prompt, open Command Prompt:

$ cd to/the/script
$ python The_Cleaners.py




