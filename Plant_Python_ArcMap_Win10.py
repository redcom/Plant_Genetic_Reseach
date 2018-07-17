#!/usr/bin/env python
import sys
import os
import numpy as np
import csv
import Tkinter
import shutil
import datetime
import random
#from PIL import Image
import ctypes
#import netCDF4
import arcpy
from comtypes.client import GetModule, CreateObject
#from Snippets import GetStandaloneModules, InitStandalone
#from typing import Union


def Globals():
    """Define global variables"""
    global dot_dot
    dot_dot = "\n.\n."

    # this var is only temporary
    global num_boxes
    num_boxes = 1
    return


class User_Interface(object):
    """This class is a TKinter-based GUI.

    utilizing grid manager, rather than pack() for now
    """

    # this allows the tk GUI to be high res for Windows 10
    if 'win' in sys.platform:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

    def __init__(self):
        """This will execute if User_Interface() is called

        Will prompt user to enter Project Name, Workspace,
        Plant Data Shapefile, and Image File
        """

        # creates a master window needed for the widgets to exist on
        self.root = Tkinter.Tk()
        self.root.wm_title("Files for PyPlant")

        # Creates widgets for a label and space to input a project name
        self.label_pname = Tkinter.Label(self.root, text="Project name")
        # grid() assigns locations. sticky moves it NSE or W within cell
        self.label_pname.grid(row=0, column=0, sticky=Tkinter.E)
        self.entrytext_pname = Tkinter.StringVar()
        # Input for data
        self.e_pname = Tkinter.Entry(
                     self.root,
                     width=80,
                     textvariable=self.entrytext_pname)
        self.e_pname.grid(row=0, column=1, columnspan=5)

        # Creates widgets for a label and space to input a workspace
        self.label_wpath = Tkinter.Label(self.root, text="Workspace Path")
        self.label_wpath.grid(row=1, column=0, sticky=Tkinter.E)
        self.entrytext_wpath = Tkinter.StringVar()
        self.e_wpath = Tkinter.Entry(
                     self.root,
                     width=80,
                     textvariable=self.entrytext_wpath)
        self.e_wpath.grid(row=1, column=1, columnspan=5)

        # Creates widgets for a label and space to input plant geo data
        self.label_geoplant = Tkinter.Label(self.root, text="Georeferenced Plant Data")
        self.label_geoplant.grid(row=2, column=0, sticky=Tkinter.E)
        self.entrytext_geoplant = Tkinter.StringVar()
        self.e_geoplant = Tkinter.Entry(
                        self.root,
                        width=80,
                        textvariable=self.entrytext_geoplant)
        self.e_geoplant.grid(row=2, column=1, columnspan=5)

        # Creates widgets for a label and space to input for dogs
        self.label_planningf = Tkinter.Label(self.root, text="Planning File")
        self.label_planningf.grid(row=4, column=0, sticky=Tkinter.E)
        self.entrytext_planningf = Tkinter.StringVar()
        self.e_planningf = Tkinter.Entry(
                         self.root,
                         width=80,
                         textvariable=self.entrytext_planningf)
        self.e_planningf.grid(row=4, column=1, columnspan=5)

        filler_1_text = "                "
        self.label_run_3 = Tkinter.Label(self.root, text=filler_1_text)
        self.label_run_3.grid(row=5, column=0, columnspan=5)

        r_col = 0
        r_row = 6
        self.label_rows = Tkinter.Label(self.root, text="Rows")
        self.label_rows.grid(row=r_row, column=r_col,
                             sticky=Tkinter.E, rowspan=5)

        self.var_row1 = Tkinter.IntVar()
        self.checkbutton_row1 = Tkinter.Checkbutton(
                              self.root,
                              text="1 plot",
                              variable=self.var_row1,
                              selectcolor="gray",
                              command=self.toggle_row1)
        self.checkbutton_row1.grid(row=r_row+1,
                                   column=r_col+1,
                                   sticky=Tkinter.W)
        self.checkbutton_row1.select()

        self.var_row2 = Tkinter.IntVar()
        self.checkbutton_row2 = Tkinter.Checkbutton(
                              self.root,
                              text="2 plot",
                              variable=self.var_row2,
                              selectcolor="gray",
                              command=self.toggle_row2)
        self.checkbutton_row2.grid(row=r_row+2,
                                   column=r_col+1,
                                   sticky=Tkinter.W)

        self.var_row4 = Tkinter.IntVar()
        self.checkbutton_row4 = Tkinter.Checkbutton(
                              self.root,
                              text="4 plot",
                              variable=self.var_row4,
                              selectcolor="gray",
                              command=self.toggle_row4)
        self.checkbutton_row4.grid(row=r_row+3,
                                   column=r_col+1,
                                   sticky=Tkinter.W)

        self.label_rows = Tkinter.Label(self.root, text="Spacing")
        self.label_rows.grid(row=r_row, column=r_col+1,
                            rowspan=5)

        self.entrytext_spacing1 = Tkinter.StringVar()
        self.e_spacing1 = Tkinter.Entry(
                        self.root,
                        width=10,
                        textvariable=self.entrytext_spacing1)
        self.e_spacing1.grid(row=r_row, column=r_col+1, sticky=Tkinter.E)

        self.entrytext_spacing2 = Tkinter.StringVar()
        self.e_spacing2 = Tkinter.Entry(
                    self.root,
                    width=10,
                    textvariable=self.entrytext_spacing2)
        self.e_spacing2.grid(row=r_row+1, column=r_col+1, sticky=Tkinter.E)

        self.entrytext_spacing3 = Tkinter.StringVar()
        self.e_spacing3 = Tkinter.Entry(
                    self.root,
                    width=10,
                    textvariable=self.entrytext_spacing3)
        self.e_spacing3.grid(row=r_row+2, column=r_col+1,sticky=Tkinter.E)

        self.entrytext_spacing4 = Tkinter.StringVar()
        self.e_spacing4 = Tkinter.Entry(
                    self.root,
                    width=10,
                    textvariable=self.entrytext_spacing4)
        self.e_spacing4.grid(row=r_row+3, column=r_col+1, sticky=Tkinter.E)

        self.entrytext_spacing5 = Tkinter.StringVar()
        self.e_spacing5 = Tkinter.Entry(
                    self.root,
                    width=10,
                    textvariable=self.entrytext_spacing5)
        self.e_spacing5.grid(row=r_row+4, column=r_col+1, sticky=Tkinter.E)

        self.var_even_spacing = Tkinter.IntVar()
        self.checkbutton_even_spacing = Tkinter.Checkbutton(
                              self.root,
                              text="Even",
                              variable=self.var_even_spacing,
                              selectcolor="gray",
                              command=self.toggle_even_spacing)
        self.checkbutton_even_spacing.grid(row=r_row+1,
                                           column=r_col+2)

        self.var_diff_spacing = Tkinter.IntVar()
        self.checkbutton_diff_spacing = Tkinter.Checkbutton(
                              self.root,
                              text="Space Saver",
                              variable=self.var_diff_spacing,
                              selectcolor="gray",
                              command=self.toggle_diff_spacing)
        self.checkbutton_diff_spacing.grid(row=r_row+3,
                                           column=r_col+2)

        self.label_pwidth = Tkinter.Label(self.root, text="Plot Width (in)")
        self.label_pwidth.grid(row=r_row+1, column=r_col+3, sticky=Tkinter.E)
        self.entrytext_pwidth = Tkinter.StringVar()
        self.e_pwidth = Tkinter.Entry(
                      self.root,
                      width=10,
                      textvariable=self.entrytext_pwidth)
        self.e_pwidth.grid(row=r_row+1, column=r_col+4,
                           columnspan=5, sticky=Tkinter.W)

        self.label_plength = Tkinter.Label(self.root, text="Plot Length (ft)")
        self.label_plength.grid(row=r_row+2, column=r_col+3, sticky=Tkinter.E)
        self.entrytext_plength = Tkinter.StringVar()
        self.e_plength = Tkinter.Entry(
                       self.root,
                       width=10,
                       textvariable=self.entrytext_plength)
        self.e_plength.grid(row=r_row+2, column=r_col+4,
                            columnspan=5, sticky=Tkinter.W)

        filler_2_text = "                "
        self.label_run_2 = Tkinter.Label(self.root, text=filler_2_text)
        self.label_run_2.grid(row=19, column=0, columnspan=5)

        # Creates a button widget for submitting inputs to program
        self.buttontext_submit = Tkinter.StringVar()
        self.buttontext_submit.set("Submit")
        # 'command' launches function to write parameters to a file
        # It will be read in later. There seems to be an issue with
        # passing inputs directly into the program.
        # assigns text and a command to the button
        self.button_submit = Tkinter.Button(
                           self.root,
                           textvariable=self.buttontext_submit,
                           command=self.write_string_to_file)
        # gives button a background color
        self.button_submit.configure(bg='Spring Green2')  # or chartruese2
        self.button_submit.grid(row=20, column=3, ipadx=35, sticky=Tkinter.W)

        # Creates a button widget for quitting the window
        self.buttontext_kill = Tkinter.StringVar()
        self.buttontext_kill.set("Kill Program")
        self.button_kill = Tkinter.Button(
                         self.root,
                         textvariable=self.buttontext_kill,
                         command=self.quit_click)
        self.button_kill.configure(bg='IndianRed2')  # or firebrick2
        self.button_kill.grid(row=20, column=0, sticky=Tkinter.E, ipadx=21)

        # Creates a button widget for reinputting inputs to program
        self.buttontext_prev = Tkinter.StringVar()
        self.buttontext_prev.set("Previous Entries")
        # 'command' launches function to write parameters to a file
        # It will be read in later. There seems to be an issue with
        # passing inputs directly into the program.
        self.button_prev = Tkinter.Button(
                         self.root,
                         textvariable=self.buttontext_prev,
                         command=self.fill_recent_entries)
        self.button_prev.configure(bg='deep sky blue2')
        self.button_prev.grid(row=20, column=1, sticky=Tkinter.W, ipadx=35)

        # These are for keyboard execution of the GUI
        # if these are to be deleted, be sure to delete
        # 'event=None' from defs
        # (keystroke, command)
        self.root.bind("<Down>", self.fill_recent_entries)
        self.root.bind("<Return>", self.write_string_to_file)
        self.root.bind("<Escape>", self.quit_click)

        # enables window to appear
        self.root.mainloop()

        return

    def toggle_row1(self):
        """When called, it delselects the other row choices"""

        if (int(self.var_row1.get()) and
           int(self.var_row2.get()) and
           int(self.var_row4.get())) == 0:
            self.checkbutton_row1.select()

        if int(self.var_row1.get()) == 1:
            self.checkbutton_row2.deselect()
            self.checkbutton_row4.deselect()
            self.checkbutton_diff_spacing.deselect()

        return

    def toggle_row2(self):
        """When called, it delselects the other row choices"""

        if (int(self.var_row1.get()) and
           int(self.var_row2.get()) and
           int(self.var_row4.get())) == 0:
            self.checkbutton_row2.select()

        if int(self.var_row2.get()) == 1:
            self.checkbutton_row1.deselect()
            self.checkbutton_row4.deselect()

        return

    def toggle_row4(self):
        """When called, it delselects the other row choices"""

        if (int(self.var_row1.get()) and
           int(self.var_row2.get()) and
           int(self.var_row4.get())) == 0:
            self.checkbutton_row4.select()

        if int(self.var_row4.get()) == 1:
            self.checkbutton_row1.deselect()
            self.checkbutton_row2.deselect()
            self.checkbutton_diff_spacing.deselect()

        return

    def toggle_even_spacing(self):
        """Enters in homogeneous spacing between the rows within a plot"""

        if int(self.var_even_spacing.get()) == 1:
            self.e_spacing1.delete(0, Tkinter.END)
            self.e_spacing1.insert(0, "10")
            self.e_spacing2.delete(0, Tkinter.END)
            self.e_spacing2.insert(0, "20")
            self.e_spacing3.delete(0, Tkinter.END)
            self.e_spacing3.insert(0, "20")
            self.e_spacing4.delete(0, Tkinter.END)
            self.e_spacing4.insert(0, "20")
            self.e_spacing5.delete(0, Tkinter.END)
            self.e_spacing5.insert(0, "10")

            self.checkbutton_diff_spacing.deselect()

        return

    def toggle_diff_spacing(self):
        """Enters in a specific spacing between the rows within a plot"""

        if int(self.var_diff_spacing.get()) == 1:
            self.e_spacing1.delete(0, Tkinter.END)
            self.e_spacing1.insert(0, "15")
            self.e_spacing2.delete(0, Tkinter.END)
            self.e_spacing2.insert(0, "10")
            self.e_spacing3.delete(0, Tkinter.END)
            self.e_spacing3.insert(0, "30")
            self.e_spacing4.delete(0, Tkinter.END)
            self.e_spacing4.insert(0, "10")
            self.e_spacing5.delete(0, Tkinter.END)
            self.e_spacing5.insert(0, "15")

            self.checkbutton_row1.deselect()
            self.checkbutton_row2.select()
            self.checkbutton_row4.deselect()
            self.checkbutton_even_spacing.deselect()

        return

    def write_string_to_file(self, event=None):
        """Command for button widget

        for given inputs, write them into a new text file and then close it
        """

        # possible for user inputted path not to have '\' at end so add it here
        workspace_path = self.entrytext_wpath.get()

        # if '\' is already there, then pass but otherwise add it to string
        if not workspace_path.endswith("\\"):
            workspace_path = workspace_path + "\\"

        # make a list of each entry that was in the text box GUI
        entered_parameters = [self.entrytext_pname.get(),
                              workspace_path,
                              self.entrytext_geoplant.get(),
                              self.entrytext_planningf.get(),
                              self.var_row1.get(),
                              self.var_row2.get(),
                              self.var_row4.get(),
                              self.var_even_spacing.get(),
                              self.var_diff_spacing.get(),
                              self.entrytext_spacing1.get(),
                              self.entrytext_spacing2.get(),
                              self.entrytext_spacing3.get(),
                              self.entrytext_spacing4.get(),
                              self.entrytext_spacing5.get(),
                              self.entrytext_pwidth.get(),
                              self.entrytext_plength.get()]

        # define a file name, without .txt
        file_name = "User_Submitted_Entries"

        # launch function to create and write to the file with the inputs
        Create_And_Write_File(file_name, entered_parameters)

        # close GUI window
        self.root.destroy()

        return

    def fill_recent_entries(self, event=None):
        """Command (to autofill) for a button widget

        this is to make users life easier with an autofill option
        by entering the last parameters the user gave into Entry widgets
        -only works if this program has been run before
        """

        # previously made file
        entry_file = "User_Submitted_Entries.txt"

        # if file exists, complete the autofill
        if os.path.exists(entry_file):

            # obtain parameters from file
            user_inputs = Read_Text_File(entry_file)

            # redefine inputs
            project_name = user_inputs[0]
            workspace = user_inputs[1]
            shapefile = user_inputs[2]
            planning_file = user_inputs[3]
            var_row1 = user_inputs[4]
            var_row2 = user_inputs[5]
            var_row4 = user_inputs[6]
            var_even_spacing = user_inputs[7]
            var_diff_spacing = user_inputs[8]
            spacing1 = user_inputs[9]
            spacing2 = user_inputs[10]
            spacing3 = user_inputs[11]
            spacing4 = user_inputs[12]
            spacing5 = user_inputs[13]
            plot_length = user_inputs[14]
            plot_width = user_inputs[15]

            # insert inputs into Entry boxes in the GUI
            # (skipped characters, variable)
            self.e_pname.insert(0, project_name)
            self.e_wpath.insert(0, workspace)
            self.e_geoplant.insert(0, shapefile)
            self.e_planningf.insert(0, planning_file)

            if int(var_even_spacing) == 1:
                self.checkbutton_row1.select()
                self.toggle_even_spacing()
            if int(var_diff_spacing) == 1:
                self.checkbutton_row1.select()
                self.toggle_diff_spacing()
            if int(var_row1) == 1:
                self.checkbutton_row1.select()
                self.toggle_row1()
            if int(var_row2) == 1:
                self.checkbutton_row2.select()
                self.toggle_row2()
            if int(var_row4) == 1:
                self.checkbutton_row4.select()
                self.toggle_row4()

            self.e_spacing1.delete(0, Tkinter.END)
            self.e_spacing1.insert(0, spacing1)
            self.e_spacing2.delete(0, Tkinter.END)
            self.e_spacing2.insert(0, spacing2)
            self.e_spacing3.delete(0, Tkinter.END)
            self.e_spacing3.insert(0, spacing3)
            self.e_spacing4.delete(0, Tkinter.END)
            self.e_spacing4.insert(0, spacing4)
            self.e_spacing5.delete(0, Tkinter.END)
            self.e_spacing5.insert(0, spacing5)
            self.e_pwidth.insert(0, plot_length)
            self.e_plength.insert(0, plot_width)

        else:
            print(entry_file + " does not exist! Enter parameters by hand")

        return

    def quit_click(self, event=None):
        """To handle quiting the window we created"""

        self.root.destroy()

        # User decides to kill program and then the scripts exits safely
        print("\nXXXXXXXXXXXX "
              "Program successfully killed by User "
              "XXXXXXXXXXXX\n")
        sys.exit(0)

        return


def Find_Rows(user_inputs):

    if int(user_inputs[0]) == 1:
        rows = 1
    elif int(user_inputs[1]) == 1:
        rows = 2
    else:
        rows = 4

    return rows


def Create_And_Write_File(file_name, data):
    """Creates and writes to a new file

    file_name -> str
    data -> list
    """

    # file_name is usually given without a type so we make it .txt
    full_file_name = file_name + ".txt"

    # create new file with full file name
    new_file = open(full_file_name, 'w+')

    # write data to the file
    for i in range(len(data)):
        new_file.write(str(data[i]) + "\n")

    # close file
    new_file.close()

    return


def Read_Text_File(file_name):
    """Read in a text file

    file_name -> str
    """

    # open the file
    x = open(file_name, 'rU')

    # read the contents and assign into list
    data_in_file = x.readlines()

    # initialize list for the forloop
    contents = []

    # strip data then append it into initialized list
    for i in range(len(data_in_file)):
        stripped_data = data_in_file[i].strip("\n")
        contents.append(stripped_data)

    x.close()

    return contents


def Create_MXD(mxd_blank):
    """Use a little ArcObjects to create new mxd

    mxd_blank -> str
    """

    # Get the Carto module
    esriCarto = GetModule(r"C:\Program Files (x86)\ArcGIS\\"
                          "Desktop10.5\com\esriCarto.olb")

    # Create a map document object
    mxdObject = CreateObject(esriCarto.MapDocument,
                             interface=esriCarto.IMapDocument)

    # Create new blank mxd file
    mxdObject.New(mxd_blank)

    # Change current view to layout
    #mxdObject.SetActiveView(mxdObject.PageLayout)

    # Save the mxd
    mxdObject.Save()

    return


def Create_ArcMap_Files(project_name, workspace, gdb_path):
    """Creates the handful of files ArcMap needs to starts a proj

    Creates a workspace folder, empty mxd, and geodatabase
    project_name -> str
    workspace -> str
    mxd -> str
    gdb_path -> str
    """

    # create folder, if it doesnt already exist
    if os.path.exists(workspace) is not True:
        os.mkdir(workspace)
        print("Created a folder at:\n" + workspace + dot_dot)
    else:
        print("Folder located at:\n" + workspace + dot_dot)

    # creates geodatabase, if it doesnt already exist
    if os.path.exists(gdb_path) is not True:
        Create_Geodatabase(project_name, workspace)
        print("Created geodatabase at:\n" + gdb_path + dot_dot)
    else:
        print("Geodatabase located at:\n" + gdb_path + dot_dot)

    return


def Create_File_Copy(file_source, workspace):
    """Creates a copy of a file that was inputed in the GUI

    file_source -> str
    workspace -> str
    """

    # divide string by folders
    split_file_path = file_source.split("\\")

    # the last option is the actual file name
    file_name = split_file_path[-1]

    file_extention = file_name.split(".")
    shapefile_id = file_extention[-1]

    # this block just copies files over
    if shapefile_id == "shp":

        shpfile_source = file_source
        shxfile_source = "\\".join(split_file_path[:-1]) \
            + "\\" + file_extention[0] + ".shx"
        dbf_source = "\\".join(split_file_path[:-1]) \
            + "\\" + file_extention[0] + ".dbf"

        shpfile_destination = workspace + "\\" + file_extention[0]  + ".shp"
        shxfile_destination = workspace + "\\" + file_extention[0] + ".shx"
        dbf_destination = workspace + "\\" + file_extention[0] + ".dbf"

        shutil.copy2(shpfile_source, shpfile_destination)

        if os.path.exists(shxfile_source):
            shutil.copy2(shxfile_source, shxfile_destination)
        else:
            print(shxfile_source + " does not exist!")

        if os.path.exists(dbf_source):
            shutil.copy2(dbf_source, dbf_destination)
        else:
            print(dbf_source + " does not exist!")

        return shpfile_destination, shxfile_destination, dbf_destination

    # combine workspace and file name for full new image address
    copy_destination = workspace + "\\" + file_name

    # make the copy of image and put it into our workspace folder
    # copy2 rather than because it copis metadata AND the permissions
    #shutil.copy2(file_source, copy_destination)

    return copy_destination


def Add_Layer(df, outLayer, transparency):
    """Add in the outLayer to the map document

    df -> arcpy._mapping.DataFrame
    outLayer -> str (shp path)
    """

    # tell ArcMap to grab new layer
    newLayer = arcpy.mapping.Layer(outLayer)
    newLayer.transparency = transparency
    print("........Layer being handled is " + str(newLayer))

    # This func actually adds the layer into arcMap
    arcpy.mapping.AddLayer(df, newLayer)
    print("............Added Layer " + str(newLayer) + " to project")

    # these commands updated the ArcMap view and the table of contents
    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()
    print("................Refreshed Views" + dot_dot)

    del df
    del newLayer
    del outLayer

    return


def Create_Polygon_Layer(df, shapefile, layer_name, field):
    """Creates a Layer of a fitted polygon to shp data

    workspacew -> str
    df -> arcpy._mapping.DataFrame
    shapefile -> str
    """
    """
    When a tool is accessed through the ArcPy site package,
    the toolbox alias where the tool is contained
    is a required suffix (arcpy._).
    Since ArcPy depends on toolbox aliases to access and
    execute the correct tool,
    aliases are extremely important when importing custom toolboxes.
    A good practice is to always define a custom toolbox's alias.
    However, if the toolbox alias is not defined,
    a temporary alias can be set as the second parameter.
    """
    """
    # Import the custom toolbox and give it an alias
    arcpy.ImportToolbox("C:\Users\William.Yingling\AppData\Roaming\\"
                        "ESRI\Desktop10.5\ArcToolbox\My Toolboxes\\"
                        "For_ModelBuilding.tbx", "polygon")

    # execute tool within custom toolbox
    arcpy.Model_polygon()
    """

    inFeatures = shapefile
    outFeatureClass = layer_name
    geometry_type = "CONVEX_HULL"  # "RECTANGLE_BY_AREA"

    # Execute our favorite ArcMap tool
    arcpy.MinimumBoundingGeometry_management(inFeatures,
                                             outFeatureClass,
                                             geometry_type,
                                             "LIST", field, "MBG_FIELDS")

    # define layer name
    # Set local variables
    out_layer = outFeatureClass + ".shp"

    #Add_Layer(df, out_layer)

    del df
    del out_layer
    return


def Create_Geodatabase(project_name, current_environment):
    """Creates a geodatabase where we would like using an ArcMap tool

    project_name -> str
    current_environment -> str
    """

    # redefine vars to match ArcMap code for clarity of parameters
    out_folder_path = current_environment
    out_name = project_name + "_Geodatabase.gdb"

    # create gdb with path name and gdb name
    gdb = arcpy.CreateFileGDB_management(out_folder_path, out_name)

    #print(out_name + " created in " + out_folder_path + dot_dot)

    del gdb

    return


def Create_Feature_Class(geodatabase_path, shapefile, geometry):
    """Creates feature class using ArcMap tool

    geodatabase_path -> str
    shapefile -> str
    geometry -> str
    """

    # define variables for arcpy tool in same manner as ArcMap
    out_path = geodatabase_path
    out_name = "Seed_plots"
    geometry_type = geometry  # "POINT" or POLYGON or POLYLINE etc
    template = shapefile
    has_m = "DISABLED"
    has_z = "DISABLED"

    # execute creation of feature class, using a try/except for safety
    try:
        arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type,
                                            template, has_m, has_z)

    except:
        print(arcpy.GetMessages())

    class_path = geodatabase_path + "\\" + out_name

    return class_path


def Add_Data_To_ArcMap(workspace, df, shapefile, layer_name):
    """Functions similarly as 'Add Data' within ArcMap

    This method will grab the data, import it, and save the layer
    workspace -> str
    df ->
    shapefile -> str
    layer_name -> str
    """

    # Set local variables
    in_layer = layer_name
    out_layer = workspace + "\\" + layer_name + ".lyr"

    # MakeFeatureLayer variables
    in_features = shapefile
    out_layer0 = layer_name

    #spatial_reference = "WGS_1984_UTM_Zone_12N"
    #arcpy.DefineProjection_management(in_features, spatial_reference)

    # Execute MakeFeatureLayer but this is a temporary creationwith SaveToFile
    # this only creates the layer, it does not import it or save it
    try:
        arcpy.MakeFeatureLayer_management(in_features, out_layer0)
        print("MakeFeatureLayer success!")

        # saves the layer from MakeFeatureLayer to make it a permanent creation
        arcpy.SaveToLayerFile_management(in_layer, out_layer)
        print("....SaveFeatureLayer success!")

        Add_Layer(df, out_layer, 75)

    except:
        # if try fails, grab the error messages
        print(arcpy.GetMessages())

    del in_layer
    del in_features
    del out_layer
    del out_layer0

    return


def Read_Plot_Shapefile(filename):
    """This is to readd in the shapefile of the plant plot data

    Here we read in .txt file with the values taken from ArcMap
    We specifically would like the Lat, Long of each point.
    Further down in the function we do some string handling to convert
    the values from strings to integers.
    Also, we do some shuffling of data to get it in compatible forms for later
    in the script
    filename -> str
    """

    # genfromtxt reads data files with ease
    # names = True says the headers are corrent for their column
    # skip_header tells np that data starts on the second line
    data = np.genfromtxt(filename, dtype=None, delimiter=";",
                         names=True, skip_header=0)

    name_joined = data['NAME']
    latitude = data['LATITUDE']
    longitude = data['LONGITUDE']
    unique_id = data['UNIQUEID']
    height = data['HEIGHT']

    #alarm_rad = data['ALARMRAD']
    #warning_rad = data['WARNINGRAD']
    #status_txt = data['STATUS_TXT']
    #visible = data['VISIBLE']

    # create an empty array
    name = [0] * len(name_joined)

    # This is to read the name category
    # this is of the format [U#,L#]
    # iterate over each pair of entries
    for i in range(len(name_joined)):

        # split the name
        element = name_joined[i].split(",")

        # U corresponds to the column
        # L corresponds to the row
        column = element[0]
        row = element[1]

        # split string into each character
        column_split = list(column)
        row_split = list(row)

        # remove the U in order to deal with the ints
        if column_split[0] == "U":
            column_split.pop(0)
        if row_split[0] == "L" or "R":
            row_split.pop(0)

        # bring the string back together, but without the letter
        column = "".join(column_split)
        row = "".join(row_split)

        try:
            # declare element as int
            column = int(column)
            row = int(row)
        except:
            pass

        # gather data into originalo format
        name_each_point = [column, row]

        # redefine the name element as the new values
        name[i] = name_each_point

    # redefine lat and long from str to float
    for j in range(len(latitude)):
        latitude[j] = float(latitude[j])
        longitude[j] = float(longitude[j])

    # declare new list as [[0,0]] * n
    # backup declaration [[0,0]] * len(latitude)
    lat_long = np.zeros((len(latitude), 2))

    # restack lat long to pair coordinates together in list
    for m in range(len(lat_long)):
        lat_long[m] = [latitude[m], longitude[m]]

    # [[lat,long], lat, long, [column,row], unique_id]
    return_package = [lat_long, latitude, longitude, name, unique_id]

    return return_package


def Write_Lat_Long(shapefile_folder, lati, longi):

    stat_analyze = shapefile_folder + "Lat_Long.csv"
    # I dont think this needed for anything...
    with open(stat_analyze, 'wb') as sa:
        lat_long_writer = csv.writer(sa, delimiter=",")

        for a in range(len(lati)):
            ll = [lati[a], longi[a]]
            lat_long_writer.writerow(ll)

        print("+++++++++++ " + stat_analyze)

    return

def Convert_Coord(length):
    """This converts inches to decimal degrees

    length -> float
    """

    km_per_deg = 111.  # km per degree. varies depending on location in world
    inches_per_km = 39370.08  # inches per km

    # make conversion from inches to degree.
    # there are ever so slight rounding errors so user beware
    length_in_degrees = length / (km_per_deg * inches_per_km)

    return length_in_degrees


def Old_Create_Surrounding_Boxes(latitude, longitude, name,
                             plot_length, plot_width):
    """This creates surrounding points around the original seed drop

    Creates a box with points like the one below

    nw--------------------ne
    \                     \
    wxnw------------------exne
    \                     \
    w---------------------e <- initial GPS point
    \                     \
    wxsw------------------exse
    \                     \
    sw--------------------se

    latitude -> list
    longitude -> list
    name -> list [float, float]
    """

    # buffers to help place points to define box
    buffer_latit = Convert_Coord(plot_width / 2.)  # typical width 80 in
    buffer_longi = Convert_Coord(plot_length * 12.)  # typical len 22 ft

    num_of_coords = len(latitude)

    # in order of being dealt with below
    # initializes empty arrays [[0,0],...]
    ne_corner = np.zeros((num_of_coords, 2))
    exne_subrow = np.zeros((num_of_coords, 2))
    e_subrow = np.zeros((num_of_coords, 2))
    exse_subrow = np.zeros((num_of_coords, 2))
    se_corner = np.zeros((num_of_coords, 2))
    sw_corner = np.zeros((num_of_coords, 2))
    wxsw_subrow = np.zeros((num_of_coords, 2))
    w_subrow = np.zeros((num_of_coords, 2))
    wxnw_subrow = np.zeros((num_of_coords, 2))
    nw_corner = np.zeros((num_of_coords, 2))

    # define the coordinates for the box corners
    # actual point is halfway between ne and se corner
    for k in range(num_of_coords):

        ne_corner_latit = latitude[k] + buffer_latit
        ne_corner_longi = longitude[k]
        ne_corner[k] = [ne_corner_latit, ne_corner_longi]

        exne_subrow_latit = latitude[k] + buffer_latit / 2.
        exne_subrow_longi = longitude[k]
        exne_subrow[k] = [exne_subrow_latit, exne_subrow_longi]

        e_subrow_latit = latitude[k]
        e_subrow_longi = longitude[k]
        e_subrow[k] = [e_subrow_latit, e_subrow_longi]

        exse_subrow_latit = latitude[k] - buffer_latit / 2.
        exse_subrow_longi = longitude[k]
        exse_subrow[k] = [exse_subrow_latit, exse_subrow_longi]

        se_corner_latit = latitude[k] - buffer_latit
        se_corner_longi = longitude[k]
        se_corner[k] = [se_corner_latit, se_corner_longi]

        sw_corner_latit = latitude[k] - buffer_latit
        sw_corner_longi = longitude[k] - buffer_longi
        sw_corner[k] = [sw_corner_latit, sw_corner_longi]

        wxsw_subrow_latit = latitude[k] - buffer_latit / 2.
        wxsw_subrow_longi = longitude[k] - buffer_longi
        wxsw_subrow[k] = [wxsw_subrow_latit, wxsw_subrow_longi]

        w_subrow_latit = latitude[k]
        w_subrow_longi = longitude[k] - buffer_longi
        w_subrow[k] = [w_subrow_latit, w_subrow_longi]

        wxnw_subrow_latit = latitude[k] + buffer_latit / 2.
        wxnw_subrow_longi = longitude[k] - buffer_longi
        wxnw_subrow[k] = [wxnw_subrow_latit, wxnw_subrow_longi]

        nw_corner_latit = latitude[k] + buffer_latit
        nw_corner_longi = longitude[k] - buffer_longi
        nw_corner[k] = [nw_corner_latit, nw_corner_longi]

    # [[0,0],...]
    box = np.array([ne_corner, exne_subrow, e_subrow, exse_subrow, se_corner,
                    sw_corner, wxsw_subrow, w_subrow, wxnw_subrow, nw_corner])

    return box


def Create_Surrounding_Boxes(latitude, longitude, name,
                             plot_length, plot_width, spacing):
    """This creates surrounding points around the original seed drop

    Creates a box with points like the one below

    nw--------------------ne
    \                     \
    wxnw------------------exne
    \                     \
    w---------------------e <- initial GPS point
    \                     \
    wxsw------------------exse
    \                     \
    sw--------------------se

    latitude -> list
    longitude -> list
    name -> list [float, float]
    """

    row1, row2, row3, row4 = Row_Define(spacing)

    top_dist = Convert_Coord(row1)
    second_dist = Convert_Coord(row2)
    third_dist = Convert_Coord(row3)
    bottom_dist = Convert_Coord(row4)

    # buffers to help place points to define box
    buffer_latit = Convert_Coord(plot_width / 2.)  # typical width 80 in
    buffer_longi = Convert_Coord(plot_length * 12.)  # typical len 22 ft

    print row1 + row2

    num_of_coords = len(latitude)

    # in order of being dealt with below
    # initializes empty arrays [[0,0],...]
    ne_corner = np.zeros((num_of_coords, 2))
    exne_subrow = np.zeros((num_of_coords, 2))
    e_subrow = np.zeros((num_of_coords, 2))
    exse_subrow = np.zeros((num_of_coords, 2))
    se_corner = np.zeros((num_of_coords, 2))
    sw_corner = np.zeros((num_of_coords, 2))
    wxsw_subrow = np.zeros((num_of_coords, 2))
    w_subrow = np.zeros((num_of_coords, 2))
    wxnw_subrow = np.zeros((num_of_coords, 2))
    nw_corner = np.zeros((num_of_coords, 2))

    # define the coordinates for the box corners
    # actual point is halfway between ne and se corner
    for k in range(num_of_coords):

        ne_corner_latit = latitude[k] + top_dist + second_dist
        ne_corner_longi = longitude[k]
        ne_corner[k] = [ne_corner_latit, ne_corner_longi]

        exne_subrow_latit = latitude[k] + second_dist
        exne_subrow_longi = longitude[k]
        exne_subrow[k] = [exne_subrow_latit, exne_subrow_longi]

        e_subrow_latit = latitude[k]
        e_subrow_longi = longitude[k]
        e_subrow[k] = [e_subrow_latit, e_subrow_longi]

        exse_subrow_latit = latitude[k] - third_dist
        exse_subrow_longi = longitude[k]
        exse_subrow[k] = [exse_subrow_latit, exse_subrow_longi]

        se_corner_latit = latitude[k] - (bottom_dist + third_dist)
        se_corner_longi = longitude[k]
        se_corner[k] = [se_corner_latit, se_corner_longi]

        sw_corner_latit = latitude[k] - (bottom_dist + third_dist)
        sw_corner_longi = longitude[k] - buffer_longi
        sw_corner[k] = [sw_corner_latit, sw_corner_longi]

        wxsw_subrow_latit = latitude[k] - third_dist
        wxsw_subrow_longi = longitude[k] - buffer_longi
        wxsw_subrow[k] = [wxsw_subrow_latit, wxsw_subrow_longi]

        w_subrow_latit = latitude[k]
        w_subrow_longi = longitude[k] - buffer_longi
        w_subrow[k] = [w_subrow_latit, w_subrow_longi]

        wxnw_subrow_latit = latitude[k] + second_dist
        wxnw_subrow_longi = longitude[k] - buffer_longi
        wxnw_subrow[k] = [wxnw_subrow_latit, wxnw_subrow_longi]

        nw_corner_latit = latitude[k] + top_dist + second_dist
        nw_corner_longi = longitude[k] - buffer_longi
        nw_corner[k] = [nw_corner_latit, nw_corner_longi]

    # [[0,0],...]
    box = np.array([ne_corner, exne_subrow, e_subrow, exse_subrow, se_corner,
                    sw_corner, wxsw_subrow, w_subrow, wxnw_subrow, nw_corner])

    return box


def Row_Define(spacing):

    row1 = spacing[0] + spacing[1] / 2.
    row2 = spacing[1] / 2. + spacing[2] / 2.
    row3 = spacing[2] / 2. + spacing[3] / 2.
    row4 = spacing[3] / 2. + spacing[4]

    print spacing
    print row1, row2, row3, row4

    return row1, row2, row3, row4


def Transpose_Plant_Plot(filename, workspace, rows):
    """Transpose the xls file

    Because planning does not always happen with North being at the
    top of the page we perform a quick matrix transposition
    to rotate it to get North being at the top of matrix.
    The xls file should be given by the user.
    filename -> str
    workspace -> str
    rows -> int
    """

    # read data from the seed planting planning csv
    planning_data = np.genfromtxt(filename, dtype=None, delimiter=",")

    # it may often need orientation
    planning_data = planning_data.transpose()

    # decplare new csv name
    transposed_csv = workspace + "\\Transposed_csv.csv"

    planned_rows = len(planning_data)
    planned_cols = len(planning_data[0])

    dims = [planned_rows, planned_cols]

    # Write to new csv so we can save it and look at it
    # using module csv to help write csv! Textbook is to thank
    with open(transposed_csv, 'wb') as csvfile:
        # enter filename and how it is to be delimited
        csvwriter = csv.writer(csvfile, delimiter=",")

        for i in range(len(planning_data)):
            csvwriter.writerow(planning_data[i])

    # initialize seed id list
    seed_id = []

    for i in range(len(planning_data)):
        # make a really long string of plant IDs
        if planning_data[i][0].lower() == "empty":
            continue

        for j in range(len(planning_data[i])):
            seed_id.append(planning_data[i][j])

    return tuple(seed_id), dims


def Create_ASCII_Attribute(shapefile, output_file):
    """Takes attribute table from shp and converts in csv/txt

    We keep similar format to ArcMap examples
    shapefile -> str
    output_file -> str
    """

    # Local variables...
    value_field = "Name;Latitude;Longitude;Height;UniqueID"

    try:
        print("here")
        # Process: Export Feature Attribute to ASCII
        arcpy.ExportXYv_stats(shapefile, value_field, "SEMI-COLON",
                              output_file, "ADD_FIELD_NAMES")
        print("here!")

    except:
        # If error occurred when running the tool, print out error message
        print(arcpy.GetMessages())

    return


def Seed_ID_Parse(seed_id, rows):
    """To parse the individual elements in seed_id for MBG later

    seed_id -> tuple
    """

    # initialize to len of seed_id
    stressor = [0] * len(seed_id)
    first_int = [0] * len(seed_id)
    species = [0] * len(seed_id)

    for s, sid in enumerate(seed_id):

        seed_split = list(sid)

        for i in range(rows):
            if len(sid) >= 3:
                stressor[s] = seed_split[0]
                first_int[s] = seed_split[1]
                species[s] = seed_split[-1]

            elif sid.lower() == ("br" or "b") or len(sid) == (2 or 1):
                stressor[s] = sid
                first_int[s] = sid
                species[s] = sid

            else:
                stressor[s] = "X"
                first_int[s] = 9
                species[s] = "X"

    return tuple(stressor), tuple(first_int), tuple(species)


def Create_Box_Points(generated_boxes, csv_file, all_boxes_file,
                      seed_id, rows, dims):
    """Create the Conditions for the bounding boxes.

    generated_boxes -> list
    shapefile_folder -> str
    seed_id -> list
    """

    stressor, first_int, species = Seed_ID_Parse(seed_id, rows)

    planned_rows = dims[0]
    planned_cols = dims[1]

    # define repeat depending on how many rows there are which
    # refers to the number of points enclosing a box
    if rows == 1:
        repeat = 10
    elif rows == 2:
        repeat = 6
    else:  # rows == 4
        repeat = 4

    # read unique ids
    with open(csv_file, 'r') as c:

        # read in table and convert to parsable list
        table_reader = list(csv.reader(c, delimiter=";"))[1:]

        unique_id = []

        for i in range(len(table_reader)):
            unique_id.append(table_reader[i][0])

    j = 0
    new_uid = []

    # reshape unique_id to fit the ranges of each experiment
    while j*planned_cols < len(unique_id):

        start_uid = j * planned_cols

        if (j+1)*planned_cols < len(unique_id):
            end_uid = (j+1) * planned_cols
        else:
            end_uid = len(unique_id)

        new_uid += unique_id[start_uid:end_uid]*rows
        j += 1

    unique_id = new_uid

    point_data = []

    # write coords of each box to new list
    for i in range(len(generated_boxes[0])):

        box_data = []

        for a in range(len(generated_boxes)):
            box_data.append(generated_boxes[a][i])

        # returns [[lat, long, subrow], [lat,long,subrow+1]...]
        data = Add_Subrow_Container(box_data, rows)

        point_data.append(data)

    seed_start = 0
    seed_end = rows * planned_cols
    p = 0
    f = 0

    unique_seed = []

    new_seed = []
    new_stressors = []
    new_first_int = []
    new_species = []

    # step through ranges of seed_id based on num of columns
    while seed_end <= len(seed_id):

        # define local rows
        seed_row = seed_id[seed_start:seed_end]
        stressors_row = stressor[seed_start:seed_end]
        first_int_row = first_int[seed_start:seed_end]
        species_row = species[seed_start:seed_end]

        # step through number of rows in each range
        while p < len(seed_row)/rows:

            seed_plot = []
            stressors_plot = []
            first_int_plot = []
            species_plot = []

            # step through each row in a plot and append its val to plot list
            while f < rows:

                seed_plot.append(seed_row[p + f*planned_cols])
                stressors_plot.append(stressors_row[p + f*planned_cols])
                first_int_plot.append(first_int_row[p + f*planned_cols])
                species_plot.append(species_row[p + f*planned_cols])
                f += 1

            # append plot list to entire field list
            new_seed.append(seed_plot)
            new_stressors.append(stressors_plot)
            new_first_int.append(first_int_plot)
            new_species.append(species_plot)

            p += 1
            f = 0

        p = 0

        # move start index to where we left off
        seed_start = seed_end

        # move ending index to next range, if possible
        if (seed_end < len(seed_id)) and \
           (seed_end + planned_cols > len(seed_id)):
            seed_end = len(seed_id)
        elif seed_end == len(seed_id):
            seed_end += 1
        else:
            seed_end += planned_cols * rows

    # restacking unique_id to write later, repeating vals for each subrow box
    for k in range(len(unique_id)):
        for m in range(repeat):
            unique_seed.append([unique_id[k]])

    seed_data = []

    # reshape to 1D array but likely not needed
    new_seed = np.reshape(
             np.array(new_seed),
             rows*len(new_seed)).tolist()
    new_stressors = np.reshape(
                  np.array(new_stressors),
                  rows*len(new_stressors)).tolist()
    new_first_int = np.reshape(
                  np.array(new_first_int),
                  rows*len(new_first_int)).tolist()
    new_species = np.reshape(
                np.array(new_species),
                rows*len(new_species)).tolist()

    # restacking seed_id, stressors, 1st_int, species to match unique_id's form
    for n in range(len(new_seed)):
        for m in range(repeat):
            seed_data.append([new_seed[n], new_stressors[n],
                              new_first_int[n], new_species[n]])

    # merge unique_id and seed_data into one list
    for c in range(len(unique_seed)):
        unique_seed[c] += seed_data[c]

    data_line = []

    # put coords and subrow info into a list
    for x in range(len(point_data)):
        for y in range(len(point_data[x])):

            point_line = [point_data[x][y][0], point_data[x][y][1],
                          point_data[x][y][2]]

            data_line.append(point_line)

    # check for correct lengths
    if len(data_line) != len(unique_seed):
        print "dataline: " + str(len(data_line)) + \
              " unique_seed: " + str(len(unique_seed))

    # start writing to all_boxes_file
    with open(all_boxes_file, 'wb') as ab:
        box_writer = csv.writer(ab, delimiter=",")

        all_boxes_header = ["Latitude", "Longitude", "Subrow", "UniqueID",
                            "Seed_ID", "Stressors", "First_Int", "Species"]
        box_writer.writerow(all_boxes_header)

        # merge coords and associated data of each point then write to a_b_f
        for z in range(len(data_line)):

            write_line = data_line[z] + unique_seed[z]

            # writes [lat, long, subrow, UID, SID, stressor, 1st_int, species]
            box_writer.writerow(write_line)

    return


def Join_Table_Seed(workspace, df, csv_file, unique_id, seed_id):
    """This functions as the Add Join tool in ArcMap

    First, we create our own csv file. Then write the unique ids taken from
    the original attribute table and also add the seed id
    which is the either the plot number or a Border plant. ( ie D###N or Br)
    The inclusion of unique IDs is imparative to join attribute tables so
    ArcMap can correctly associate to corresponding data in both tables
    Second, we convert the new csv to dbf using arcmap tools because
    ArcMap won't automatically recognize the csv as a joinable table
    Third, we take original shapefile join it with the dbf to create new layer
    Fourth, We add the new shapefile into ArcMap
    workspace -> str
    unique_id -> list
    planning_data -> list
    """

    # the header for new seed id category
    new_headers = ["UniqueID", "SeedID"]

    csv_to_join = csv_file

    # using module csv to help write csv! Textbook is to thank
    with open(csv_to_join, 'wb') as csvfile:
        # enter filename and how it is to be delimited
        csvwriter_0 = csv.writer(csvfile, delimiter=";")

        for i in range(len(unique_id)):  # usually seed_id
            if i == 0:
                    csvwriter_0.writerow(new_headers)

            both_ids = [str(unique_id[i]), str(seed_id[i])]
            csvwriter_0.writerow(both_ids)

    # Set local variables list, str
    inTables = [csv_to_join]
    outLocation = workspace + "\Shapefile_Handling"

    # convert csv to dbf with ArcMap
    arcpy.TableToDBASE_conversion(inTables, outLocation)

    # Set environment settings
    arcpy.env.qualifiedFieldNames = False

    # Set local variables
    inFeatures = workspace + "\PointFeature.shp"
    layerName = "SEED_PLOTS_join"
    joinTable = workspace + "\Shapefile_Handling\Table_to_join.dbf"
    joinField = "UNIQUEID"
    outFeature = workspace + "\SEED_PLOTS_join.shp"

    CSV_to_Layer(inFeatures, layerName, joinField, joinTable, outFeature)

    Add_Layer(df, outFeature, 75)

    del df
    del inFeatures
    del layerName
    del joinField
    del joinTable
    del outFeature
    del inTables
    del outLocation

    return


def Add_Plot_Polys(df, all_boxes_file, shapefile_folder, spatial_reference):

    # Set local variables list, str
    inTables = [all_boxes_file]
    outLocation = shapefile_folder

    # convert csv to dbf with ArcMap
    arcpy.TableToDBASE_conversion(inTables, outLocation)

    # string manipulation to obtain path without extension
    split_box_name = all_boxes_file.split(".")
    box_no_extension = split_box_name[:-1]
    table_path = ".".join(box_no_extension)

    # Set the local variables
    in_Table = table_path + ".dbf"
    y_coords = "Latitude"
    x_coords = "Longitude"
    out_Layer = "All_Plots"
    saved_Layer = table_path + ".lyr"

    try:
        # Make the XY event layer...
        arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords,
                                          out_Layer, spatial_reference)
    except:
        print(arcpy.GetMessages())
    # Save to a layer file
    arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)

    # Add layer to the df
    Add_Layer(df, out_Layer, 75)

    # define a name for the poly to be made
    poly_layer_name = shapefile_folder + out_Layer + "_Polygons"

    field = "Subrow", "UniqueID", "Seed_ID",

    # Create a layer of polygon surrounding shp file.
    Create_Polygon_Layer(df, saved_Layer, poly_layer_name, field)

    Add_Layer(df, poly_layer_name + ".shp", 75)

    return


def CSV_to_Layer(inFeatures, layerName, joinField, joinTable, outFeature):
    """Create an Event from CSV, join tables, then save it in to df

    df -> arcpy._mapping.DataFrame
    inFeatures -> str .shp
    layerName -> str
    joinField -> str .dbf
    joinTable -> str
    outFeature -> str .shp
    """

    # Create a feature layer from the vegtype featureclass
    arcpy.MakeFeatureLayer_management(inFeatures,  layerName)
    print("................Made Feature Layer")

    # Join the feature layer to a table
    arcpy.AddJoin_management(layerName, joinField, joinTable, joinField)
    print("................Add Join completed")

    # Select desired features from veg_layer
    arcpy.SelectLayerByAttribute_management(layerName, "NEW_SELECTION")
    print("................Selected Layer " + layerName)

    # Copy the layer to a new permanent feature class
    arcpy.CopyFeatures_management(layerName, outFeature)
    print("................Copied Features " + outFeature)

    del inFeatures
    del layerName
    del joinField
    del joinTable

    return


def Add_Subrow_Container(generated_boxes, subrow_container):
    """This is to append a subrow value to the generated box points.

    The value of 1,2, or 4 is assigned to the boxes so as to differentiate
    that the seed may not be consistent within the entire plot.
    This assists with the drawing of each polygon around/within each plot.
    generated_boxes -> list
    subrow_container -> int
    """

    ne_corner = generated_boxes[0]
    exne_subrow = generated_boxes[1]
    e_subrow = generated_boxes[2]
    exse_subrow = generated_boxes[3]
    se_corner = generated_boxes[4]
    sw_corner = generated_boxes[5]
    wxsw_subrow = generated_boxes[6]
    w_subrow = generated_boxes[7]
    wxnw_subrow = generated_boxes[8]
    nw_corner = generated_boxes[9]

    if subrow_container == 1:

        # Box 1
        ne_corner_wtype = np.append(ne_corner, 1)
        exne_subrow_wtype = np.append(exne_subrow, 1)
        e_subrow_wtype = np.append(e_subrow, 1)
        exse_subrow_wtype = np.append(exse_subrow, 1)
        se_corner_wtype = np.append(se_corner, 1)
        sw_corner_wtype = np.append(sw_corner, 1)
        wxsw_subrow_wtype = np.append(wxsw_subrow, 1)
        w_subrow_wtype = np.append(w_subrow, 1)
        wxnw_subrow_wtype = np.append(wxnw_subrow, 1)
        nw_corner_wtype = np.append(nw_corner, 1)

        data = [ne_corner_wtype, exne_subrow_wtype,
                e_subrow_wtype, exse_subrow_wtype,
                se_corner_wtype, sw_corner_wtype,
                wxsw_subrow_wtype, w_subrow_wtype,
                wxnw_subrow_wtype, nw_corner_wtype]

    if subrow_container == 2:

        # Box 1
        ne_corner_wtype = np.append(ne_corner, 1)
        exne_subrow_wtype = np.append(exne_subrow, 1)
        e_subrow_1 = np.append(e_subrow, 1)
        w_subrow_1 = np.append(w_subrow, 1)
        wxnw_subrow_wtype = np.append(wxnw_subrow, 1)
        nw_corner_wtype = np.append(nw_corner, 1)

        # Box 2
        e_subrow_2 = np.append(e_subrow, 2)
        exse_subrow_wtype = np.append(exse_subrow, 2)
        se_corner_wtype = np.append(se_corner, 2)
        sw_corner_wtype = np.append(sw_corner, 2)
        wxsw_subrow_wtype = np.append(wxsw_subrow, 2)
        w_subrow_2 = np.append(w_subrow, 2)

        data = [ne_corner_wtype, exne_subrow_wtype,
                e_subrow_1, w_subrow_1,
                wxnw_subrow_wtype, nw_corner_wtype,
                e_subrow_2, exse_subrow_wtype,
                se_corner_wtype, sw_corner_wtype,
                wxsw_subrow_wtype, w_subrow_2]

    if subrow_container == 4:

        # Box 1
        ne_corner_wtype = np.append(ne_corner, 1)
        exne_subrow_1 = np.append(exne_subrow, 1)
        wxnw_subrow_1 = np.append(wxnw_subrow, 1)
        nw_corner_wtype = np.append(nw_corner, 1)

        # Box 2
        exne_subrow_2 = np.append(exne_subrow, 2)
        e_subrow_2 = np.append(e_subrow, 2)
        w_subrow_2 = np.append(w_subrow, 2)
        wxnw_subrow_2 = np.append(wxnw_subrow, 2)

        # Box 3
        e_subrow_3 = np.append(e_subrow, 3)
        exse_subrow_3 = np.append(exse_subrow, 3)
        wxsw_subrow_3 = np.append(wxsw_subrow, 3)
        w_subrow_3 = np.append(w_subrow, 3)

        # Box 4
        exse_subrow_4 = np.append(exse_subrow, 4)
        se_corner_wtype = np.append(se_corner, 4)
        sw_corner_wtype = np.append(sw_corner, 4)
        wxsw_subrow_4 = np.append(wxsw_subrow, 4)

        data = [ne_corner_wtype, exne_subrow_1,
                wxnw_subrow_1, nw_corner_wtype,
                exne_subrow_2, e_subrow_2,
                w_subrow_2, wxnw_subrow_2,
                e_subrow_3, exse_subrow_3,
                wxsw_subrow_3, w_subrow_3,
                exse_subrow_4, se_corner_wtype,
                sw_corner_wtype, wxsw_subrow_4]

    return data


def Parameters_Executed(housing_folder, inputs):
    """Provide a history of what was executed

    housing_folder -> str
    inputs -> list of str
    """

    parameters = []

    now = datetime.datetime.now()
    now_time = str(now.hour) + ":" + str(now.minute)
    now_date = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

    parameters.append("##\n## A Catalog of the Parameters\n"
                      "## used in the lastest execution\n"
                      "## of Plant_Python_ArcMap.py\n##")
    parameters.append(" ")
    parameters.append("## If 'Executed' appears in a line, the associated\n"
                      "## number is a Binary representation of True/False")
    parameters.append(" ")
    parameters.append("Time: " + now_time + "    Date: " + now_date)
    parameters.append(" ")

    parameters.append("Project Name: " + inputs[0])
    parameters.append("Workspace: " + inputs[1])
    parameters.append("Shapefile Copied: " + inputs[2])
    parameters.append(" ")

    parameters.append("Planning File: " + inputs[3])
    parameters.append("Rows: " + inputs[4])
    parameters.append("Plot Length in ft: " + inputs[5])
    parameters.append("Plot Width in inches: " + inputs[6])

    Create_And_Write_File(housing_folder + "\Parameters_Executed", parameters)

    return


def Compose_Polygons(df, spatial_reference, shapefile_folder, polygon_file):
    """Makes the polygons from the all_boxes_file.

    df -> arcmap dataframae object
    spatial_reference -> arcmap sr object
    shapefile_folder -> str
    polygon_file -> str
    """

    # Set local variables list, str
    inTables = [polygon_file]
    outLocation = shapefile_folder

    # convert csv to dbf with ArcMap
    arcpy.TableToDBASE_conversion(inTables, outLocation)

    # string manipulation to obtain path without extension
    split_box_name = polygon_file.split(".")
    box_no_extension = split_box_name[:-1]
    table_path = ".".join(box_no_extension)

    split_path = split_box_name[-2].split("\\")

    #try:
    # Set the local variables
    in_Table = table_path + ".dbf"
    y_coords = "Latitude"
    x_coords = "Longitude"
    out_Layer = split_path[-1]
    saved_Layer = table_path + ".lyr"

    # Make the XY event layer...
    arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords,
                                      out_Layer, spatial_reference)

    # Save to a layer file
    arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)

    # Add layer to the df
    #Add_Layer(df, out_Layer, 75)

    # define a name for the poly to be made
    poly_layer_name = shapefile_folder + out_Layer + "_Polygon"

    field = ["Species", "Stressors"]

    # Create a layer of polygon surrounding shp file.
    Create_Polygon_Layer(df, saved_Layer, poly_layer_name, field)

    Add_Layer(df, poly_layer_name + ".shp", 75)

    return


def Organize_Layers(mxd, df):
    """Organize the df layers so they ordered to our liking

    mxd -> map document
    df -> arcpy._mapping.DataFrame
    """

    for l, lyr in enumerate(arcpy.mapping.ListLayers(mxd, "", df)):

        if l == 0:
            refLayer = lyr
        if lyr.name.lower() == "all_plots_polygons":
            movePlotLayer = lyr
            ext = lyr.getExtent()
            df.extent = ext
        if lyr.name.lower() == "seed_plots_join":
            moveSeedLayer = lyr

    #arcpy.mapping.MoveLayer(df, refLayer, movePlotLayer, "BEFORE")
    #arcpy.mapping.MoveLayer(df, refLayer, moveSeedLayer, "BEFORE")
    #arcpy.mapping.MoveLayer(df, refLayer, movePlotLayer, "BEFORE")

    # turn off all layers from being visible
    for lyr in arcpy.mapping.ListLayers(mxd, "*", df):

        lyr.showLabels = False
        lyr.visible = False

    # turn on the POLY layers (species and first int layers)
    for yrl in arcpy.mapping.ListLayers(mxd, "*POLY*", df):

        yrl.visible = True

    # turn off the Br layers since theyre not needed
    #for rly in arcpy.mapping.ListLayers(mxd, "*_Br_*", df):

    #    rly.visible = False

    # turn on and label the all_plots_polygons file
    for lll in arcpy.mapping.ListLayers(mxd, "*Polygons", df):

        lll.visible = True
        lll.showLabels = True

        # labels default to first column so change it to SEED_ID column
        lblClass = lll.labelClasses[0]
        lblClass.expression = "[SEED_ID]"



    return


def Dummy_Check(generated_boxes, seed_id):
    """Checks if the two lists are of matching length.

    If the lists are of different lengths then create dummy variables
    within seed_id marked X999X. if the lists match,  do nothing.
    generated_boxes -> list
    seed_id -> list
    """

    # We need to match number of bounding boxes so add on dummy vars
    if len(generated_boxes) != len(seed_id):
        # this only functions for gb > seed_id
        dummy_len = len(generated_boxes) - len(seed_id)
        dummys = tuple(["X999X"] * dummy_len)
        seed_id = seed_id + dummys

    return seed_id


def Rotate_Data_View(mxd, df):
    """Used to zoom in or rotate the view of the data.

    mxd -> map document
    df -> dataframe object
    """

    data_frame = arcpy.mapping.ListDataFrames(mxd)[0]

    # Switch to data view
    mxd.activeView = data_frame.name

    # for every layer, scale it to specified number
    for df in arcpy.mapping.ListDataFrames(mxd):
        #df.rotation = 90
        df.scale = 100
        arcpy.RefreshActiveView()

    # refresh viewer and table of contents
    arcpy.RefreshTOC()
    arcpy.RefreshActiveView()

    return


def Export_PDF(mxd, workspace, project_name):
    """Export ArcMap data to a PDF.

    mxd -> map document
    workspace -> str
    project_name -> str
    """

    print("Exporting to PDF\n.\n")

    pdf_name = workspace + "\\" + project_name + ".pdf"
    arcpy.mapping.ExportToPDF(mxd, pdf_name)

    return


def Create_Polygon_Files(df, spatial_reference,
                         shapefile_folder, all_boxes_file):
    """Write files where points fall are of similar stressors or 1st int

    df -> dataframe arcmap object
    spatial_reference -> reference frame
    shapefile_folder -> str
    all_boxes_file -> str
    """

    #species_list = []
    stressors_list = []
    first_int_list = []

    polygon_files = []

    with open(all_boxes_file, "rU") as abf:
        csvreader = list(csv.reader(abf, delimiter=","))

        # find indexes that match Species, stressors, first_int
        for h, header in enumerate(csvreader[0]):

            #if header == "Species":
            #    species_index = h
            if header == "Stressors":
                stressors_index = h
            if header == "First_Int":
                first_int_index = h

        # add each distinct value to list
        for p, point in enumerate(csvreader[1:]):

            #if (point[species_index] not in species_list) and \
            #   (point[species_index].lower() != "br"):
            #    species_list.append(point[species_index])

            if (point[stressors_index] not in stressors_list) and \
               (point[stressors_index].lower() != "br"):
                stressors_list.append(point[stressors_index])

            if (point[first_int_index] not in first_int_list) and \
               (point[first_int_index].lower() != "br"):
                first_int_list.append(point[first_int_index])
        """
        for i in range(len(species_list)):

            species_file = shapefile_folder + "\Species_" + species_list[i] + ".csv"

            polygon_files.append(species_file)

            with open(species_file, "wb") as sf:
                csvwriter = csv.writer(sf, delimiter=",")
                csvwriter.writerow(csvreader[0])

                for r, row in enumerate(csvreader):
                    if row[species_index] == species_list[i]:

                        csvwriter.writerow(row)
        """
        # put grouped stressors into unique files.
        for i in range(len(stressors_list)):

            stressors_file = shapefile_folder + "\Stressors_" + \
                stressors_list[i] + ".csv"

            polygon_files.append(stressors_file)

            with open(stressors_file, "wb") as sf:

                csvwriter = csv.writer(sf, delimiter=",")
                csvwriter.writerow(csvreader[0])

                for r, row in enumerate(csvreader):
                    if row[stressors_index] == stressors_list[i]:
                        csvwriter.writerow(row)

        # put grouped first_int into unique files.
        for i in range(len(first_int_list)):

            first_int_file = shapefile_folder + "\First_Int_" + \
                first_int_list[i] + ".csv"

            polygon_files.append(first_int_file)

            with open(first_int_file, "wb") as sf:

                csvwriter = csv.writer(sf, delimiter=",")
                csvwriter.writerow(csvreader[0])

                for r, row in enumerate(csvreader):
                    if row[first_int_index] == first_int_list[i]:

                        csvwriter.writerow(row)

    return polygon_files


###############################################################################
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Main Function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
###############################################################################
def main():
    
    # This needs to be run the first time the script is executed
    #GetStandaloneModules()
    #InitStandalone()

    Globals()

    # Asks user for the inputs they would like to specify
    User_Interface()

    # read in the text file of user inputs
    user_inputs = Read_Text_File("User_Submitted_Entries.txt")

    # redefine the inputs with appropriate names
    project_name = user_inputs[0]
    workspace = user_inputs[1]
    shapefile_copy = user_inputs[2]
    planning_file = user_inputs[3]
    rows = Find_Rows(user_inputs[4:7])
    var_even_spacing = user_inputs[7]
    var_diff_spacing = user_inputs[8]
    spacing = [float(user_inputs[9]), float(user_inputs[10]),
               float(user_inputs[11]), float(user_inputs[12]),
               float(user_inputs[13])]
    plot_width = int(user_inputs[14])
    plot_length = int(user_inputs[15])

    print("*****************\ Begin creation of project " + project_name +
          " /*****************" + dot_dot)

    # Overwrites files that may have the same name
    arcpy.env.overwriteOutput = True

    # Define an arcpy workspace. Backslashes would be removed at end by default
    arcpy.env.workspace = workspace + project_name

    mxd_blank = arcpy.env.workspace + "\\" + project_name + "_blank.mxd"
    mxd_name = arcpy.env.workspace + "\\" + project_name + ".mxd"
    geodatabase_path = arcpy.env.workspace + "\\" + \
        project_name + "_Geodatabase.gdb"

    # Create the gdb, mxd, and folder to store it in with arcmap
    Create_ArcMap_Files(project_name, arcpy.env.workspace, geodatabase_path)

    shapefile_folder = str(arcpy.env.workspace) + "\Shapefile_Handling\\"
    csv_file = shapefile_folder + "Table_to_join.csv"
    all_boxes_file = shapefile_folder + "All_generated_boxes.csv"

    if os.path.exists(shapefile_folder) is False:
        os.mkdir(shapefile_folder)

    Parameters_Executed(arcpy.env.workspace, user_inputs)

    # copy over the shp, shx, and dbf files from user directory
    shapefile, shx_path, dbf_path = Create_File_Copy(shapefile_copy,
                                                     arcpy.env.workspace)

    if os.path.exists(mxd_blank):
        os.remove(mxd_blank)

    if os.path.exists(mxd_name):
        os.remove(mxd_name)
        #print("File removed!")

    Create_MXD(mxd_blank)

    # define the map document to be accessed
    mxd = arcpy.mapping.MapDocument(mxd_blank)

    # define data frame to be worked with
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    # give df a reference frame
    # 4326 is the WKID for the Geo Coord Sys WGS 1984
    #df.spatialReference = 4326

    # WGS_1984_UTM_Zone_12N (Bill's projection system)
    df.spatialReference = 32612

    # Need to define a projection system for all the data
    spatial_reference = arcpy.SpatialReference(4326)

    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)

    print("Data Frame being dealt with is " + str(df) + dot_dot)

    attribute_output = shapefile_folder + "\\Attribute_table_ASCII.txt"

    # Create a txt file of the attribute table of the shapefile
    Create_ASCII_Attribute(shapefile, attribute_output)

    # read the attributes of the shapefile
    coords = Read_Plot_Shapefile(attribute_output)

    lat_long = coords[0]
    lati = coords[1]
    longi = coords[2]
    name = coords[3]
    unique_id = coords[4]

    Write_Lat_Long(shapefile_folder, lati, longi)

    # execute box generating function
    generated_boxes = Create_Surrounding_Boxes(lati, longi,
                                               name, plot_length,
                                               plot_width, spacing)

    # Transpose the planning xls file so north is facing up
    seed_id, dims = Transpose_Plant_Plot(
                  planning_file, arcpy.env.workspace, rows)

    seed_id = Dummy_Check(generated_boxes[0], seed_id)

    # join the attribute table of the shapefile and seed_ids
    Join_Table_Seed(arcpy.env.workspace, df, csv_file, unique_id, seed_id)

    Create_Box_Points(generated_boxes, csv_file, all_boxes_file,
                      seed_id, rows, dims)

    Add_Plot_Polys(df, all_boxes_file, shapefile_folder, spatial_reference)

    polygon_files = Create_Polygon_Files(df, spatial_reference,
                                         shapefile_folder, all_boxes_file)

    for polygon_path in polygon_files:
        Compose_Polygons(df, spatial_reference, shapefile_folder, polygon_path)

    Organize_Layers(mxd, df)

    # need to save a copy to new document with
    mxd.saveACopy(mxd_name)

    Rotate_Data_View(mxd, df)
    Export_PDF(mxd, arcpy.env.workspace, project_name)
    print("Created new and updated project success!")

    del df
    del shapefile_copy
    del shapefile
    del arcpy.env.workspace
    del spatial_reference

    del mxd
    

if __name__ == '__main__':
    main()

# Will Yingling
# Biological Science Technician, USDA
# April 2017
