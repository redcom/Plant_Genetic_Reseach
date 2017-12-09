import numpy as np
from numpy import random as npr
import csv
import os


def Globals():
    global num_plots
    num_plots = 185

    global scalar
    scalar = 5

    return


def Plot_Check(plot_id):

    plot_split = list(plot_id)

    if plot_split[0] == 'W':
        return 1.
    if plot_split[0] == 'D':
        return .8
    if plot_split[0] == 'Z':
        return .6

    return


def Create_Pep(housing_folder, plot_ids, run):

    csv_file = housing_folder + "\Pep_plots.csv"

    with open(csv_file, 'wb') as cf:
        writer = csv.writer(cf, delimiter=',')
        header = ["FID", "Sensor", "CropHeight", "PLOT"]
        writer.writerow(header)

        pep_sensors = ["Pepperl_1", "Pepperl_2", "Pepperl_3", "Pepperl_4"]

        # (Stressors*Species*Global)*Sensors*Scalar
        amt_of_data = len(plot_ids)*len(pep_sensors)*scalar

        rand_pos = np.random.random(1)
        rand_pos = rand_pos[0]

        rand_neg = np.random.random(1)
        rand_neg = rand_neg[0] * -1.

        height = 15 * run * rand_pos

        rand_vals = npr.normal(height, 7.5, amt_of_data)

        for i in range(amt_of_data):

            rand_sensor = npr.choice(pep_sensors, 1)
            rand_plot = npr.choice(plot_ids, 1)

            chosen_plot = rand_plot[0]
            multiplier = Plot_Check(chosen_plot)

            row = [i, rand_sensor[0], float(round(rand_vals[i]*multiplier, 4)),
                   chosen_plot]

            writer.writerow(row)

    return


def Create_Honey(housing_folder, plot_ids, run):

    csv_file = housing_folder + "\Honey_plots.csv"

    with open(csv_file, 'wb') as cf:
        writer = csv.writer(cf, delimiter=',')
        header = ["FID", "Sensor", "CropHeight", "PLOT"]
        writer.writerow(header)

        honey_sensors = ["Honeywell_1", "Honeywell_2",
                         "Honeywell_3", "Honeywell_4"]

        # (Stressors*Species*Global)*Sensors*Scalar
        amt_of_data = len(plot_ids)*len(honey_sensors)*scalar

        rand_pos = np.random.random(1)
        rand_pos = rand_pos[0]

        rand_neg = np.random.random(1)
        rand_neg = rand_neg[0] * -1.

        height = 13 * run * rand_pos

        rand_vals = npr.normal(height, 7.5, amt_of_data)

        for i in range(amt_of_data):

            rand_sensor = npr.choice(honey_sensors, 1)
            rand_plot = npr.choice(plot_ids, 1)

            chosen_plot = rand_plot[0]
            multiplier = Plot_Check(chosen_plot)

            row = [i, rand_sensor[0], float(round(rand_vals[i]*multiplier, 4)),
                   chosen_plot]

            writer.writerow(row)

    return


def Create_IRT(housing_folder, plot_ids, nadir_forward, run):

    if nadir_forward == "nadir":
        csv_file = housing_folder + "\IRT_nadir_plots.csv"
    else:
        csv_file = housing_folder + "\IRT_forward_plots.csv"

    with open(csv_file, 'wb') as cf:
        writer = csv.writer(cf, delimiter=',')
        header = ["FID", "Sensor", "Target_Cel", "PLOT"]
        writer.writerow(header)

        if nadir_forward == "nadir":
            irt_sensors = ["IRT_5", "IRT_6", "IRT_7", "IRT_8"]
        else:
            irt_sensors = ["IRT_1", "IRT_2", "IRT_3", "IRT_4"]

        # (Stressors*Species*Global)*Sensors*Scalar / div by 2 bc two files
        amt_of_data = len(plot_ids)*len(irt_sensors)*scalar/2

        rand_pos = np.random.random(1)
        rand_pos = rand_pos[0]

        rand_neg = np.random.random(1)
        rand_neg = rand_neg[0] * -1.

        height = 20. * rand_pos

        rand_vals = npr.normal(height, 4., amt_of_data)

        for i in range(amt_of_data):

            rand_sensor = npr.choice(irt_sensors, 1)
            rand_plot = npr.choice(plot_ids, 1)

            chosen_plot = rand_plot[0]
            multiplier = Plot_Check(chosen_plot)

            row = [i, rand_sensor[0], float(round(rand_vals[i]*multiplier, 4)),
                   chosen_plot]

            writer.writerow(row)

    return


def Create_CC(housing_folder, plot_ids, run):

    csv_file = housing_folder + "\CC_plots.csv"

    with open(csv_file, 'wb') as cf:
        writer = csv.writer(cf, delimiter=',')
        header = ["FID", "Sensor", "CIRE", "MTCI", "CCCI", "CCCIA", "CI800",
                  "DATT", "DATTA", "NDARE", "NDRE", "NDRRE", "NDVIA",
                  "NDVIR", "NVG2", "NVG800", "PRI", "PLOT"]

        writer.writerow(header)

        cc_sensors = ["CC_1", "CC_2", "CC_3", "CC_4",
                      "CC_5", "CC_6", "CC_7", "CC_8"]

        # (Stressors*Species*Global)*Sensors*Scalar
        amt_of_data = len(plot_ids)*len(cc_sensors)*scalar

        rand_cire = npr.normal(0.1, 0.1, amt_of_data)
        rand_mtci = npr.normal(0.65, 0.15, amt_of_data)
        rand_ccci = npr.normal(0.35, 0.1, amt_of_data)
        rand_cccia = npr.normal(0.3, 0.1, amt_of_data)
        rand_ci800 = npr.normal(0.8, 0.1, amt_of_data)
        rand_datt = npr.normal(0.4, 0.1, amt_of_data)
        rand_datta = npr.normal(0.35, 0.1, amt_of_data)
        rand_ndare = npr.normal(0.2, 0.05, amt_of_data)
        rand_ndre = npr.normal(0.1, 0.05, amt_of_data)
        rand_ndrre = npr.normal(0.1, 0.05, amt_of_data)
        rand_ndvia = npr.normal(0.1, 0.05, amt_of_data)
        rand_ndvir = npr.normal(0.25, 0.1, amt_of_data)
        rand_nvg2 = npr.normal(0.35, 0.05, amt_of_data)
        rand_nvg800 = npr.normal(0.45, 0.1, amt_of_data)
        rand_pri = npr.normal(0.2, 0.25, amt_of_data)

        for i in range(amt_of_data):

            rand_sensor = npr.choice(cc_sensors, 1)
            rand_plot = npr.choice(plot_ids, 1)

            chosen_plot = rand_plot[0]
            multiplier = Plot_Check(chosen_plot)

            row = [i, rand_sensor[0], rand_cire[i]*multiplier,
                   rand_mtci[i]*multiplier, rand_ccci[i]*multiplier,
                   rand_cccia[i]*multiplier, rand_ci800[i]*multiplier,
                   rand_datt[i]*multiplier, rand_datta[i]*multiplier,
                   rand_ndare[i]*multiplier, rand_ndre[i]*multiplier,
                   rand_ndrre[i]*multiplier, rand_ndvia[i]*multiplier,
                   rand_ndvir[i]*multiplier, rand_nvg2[i]*multiplier,
                   rand_nvg800[i]*multiplier, rand_pri[i]*multiplier,
                   chosen_plot]

            writer.writerow(row)

    return


def Create_Plot_IDS(housing_folder):

    stressors = ['W','D']  #,'Z']
    species = ['Z', 'Y']  #,'L','C']

    plot_ids = []

    for i in range(len(species)):
        for j in range(len(stressors)):
            for k in range(100, num_plots):

                plot_name = stressors[j] + str(k) + species[i]

                plot_ids.append(plot_name)

    return plot_ids


def main():

    Globals()

    total_runs = 6

    for run in range(total_runs):

        housing_folder = r"C:\Users\William.Yingling\Scripts\ArcMap_" + \
                    "Projects\Fake_Data_4_Row\Fake_Run0" + str(run) + r"_Vesta"

        if os.path.exists(housing_folder) is True:
            os.rmdir(housing_folder)

        os.mkdir(housing_folder)

        plot_ids = Create_Plot_IDS(housing_folder)

        Create_Pep(housing_folder, plot_ids, run)
        Create_Honey(housing_folder, plot_ids, run)

        Create_IRT(housing_folder, plot_ids, "forward", run)
        Create_IRT(housing_folder, plot_ids, "nadir", run)

        Create_CC(housing_folder, plot_ids, run)


if __name__ == '__main__':
    main()