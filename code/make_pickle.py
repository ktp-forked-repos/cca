import numpy as np
import matplotlib.pyplot as plt
import time
from scipy import ndimage
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import pickle
import itertools
import sys
import os
import warnings

warnings.filterwarnings(action="ignore", module="scipy", message="^internal gelsd")

cca_dir = '/Users/tomlinsonk/Projects/Research/cca/'

def main(neighborhood, size):
    vn = neighborhood == 'vn'

    print('Processing {0}x{0} {1} data...'.format(size, 'von Neumann' if vn else 'Moore'))
    k_range = range(7, 16) if vn else range(11, 27)

    debris_lengths = {k: [] for k in k_range}
    droplet_lengths = {k: [] for k in k_range}
    defect_lengths = {k: [] for k in k_range}


    if size == 128:
        if vn:
            min_step = {7:6, 8:8, 9:13, 10:18, 11:26, 12:44, 13:79, 14:128, 15: 160}
            widths = {7:5, 8:11, 9:17, 10:21, 11:27, 12:51, 13:71, 14:61, 15: 101}
        else:
            min_step = {11: 11, 12: 14, 13: 19, 14: 22, 15: 27, 16: 36, 17: 43, 18: 55, 19: 67, 20: 72, 21: 86, 22: 104, 23: 125, 24:161, 25: 197, 26: 217}
            widths = {11: 5, 12: 9, 13: 15, 14: 15, 15: 15, 16: 25, 17: 25, 18: 31, 19: 41, 20:51, 21: 61, 22: 81, 23: 91, 24:101, 25: 101, 26: 101}
    elif size == 256:
        if vn:
            min_step = {7:6, 8:8, 9:13, 10:18, 11:26, 12:44, 13:79, 14:128, 15: 160}
            widths = {7:5, 8:7, 9:11, 10:13, 11:17, 12:21, 13:41, 14:61, 15: 81}
        else:
            min_step = {11: 10, 12: 14, 13: 19, 14: 22, 15: 27, 16: 36, 17: 43, 18: 55, 19: 67, 20: 72, 21: 86, 22: 104, 23: 125, 24:161, 25: 197, 26: 217}
            widths = {11: 5, 12: 5, 13: 5, 14: 11, 15: 11, 16: 17, 17: 25, 18: 25, 19: 31, 20: 37, 21: 41, 22: 49, 23: 51, 24:71, 25: 91, 26: 101}
    elif size == 512:
        if vn:
            min_step = {7:6, 8:8, 9:13, 10:18, 11:26, 12:44, 13:79, 14:128, 15: 160}
            widths = {7:5, 8:11, 9:17, 10:21, 11:27, 12:51, 13:71, 14:61, 15: 101}
        else:
            min_step = {11: 10, 12: 14, 13: 19, 14: 22, 15: 27, 16: 36, 17: 43, 18: 55, 19: 67, 20: 72, 21: 86, 22: 104, 23: 125, 24:161, 25: 197, 26: 217}
            widths = {11: 5, 12: 5, 13: 5, 14: 11, 15: 11, 16: 17, 17: 25, 18: 25, 19: 31, 20: 37, 21: 41, 22: 49, 23: 51, 24:71, 25: 91, 26: 101}
    else:
        print('Size must be one of: 128, 256, 512')
        exit(1)

    print('Loading file...')
    data_file = cca_dir + 'data/combined/{}_{}_neighbor_diff_data.csv'.format(size, neighborhood)
    raw_data = np.loadtxt(data_file, dtype=int, delimiter=',')

    data = {k: [] for k in k_range}
    for row in raw_data:
        if row[0] in k_range:
            data[row[0]].append(row[2:])


    phase_points = {k: [] for k in k_range}

    showing = False
    print('Finding phase lengths...')
    for k in k_range:
        print('Unique trials:', len(set(tuple(trial) for trial in data[k])))

        for trial in range(len(data[k])):

            min_diff = np.argmin(data[k][trial])
            
            # deriv1 = np.gradient(means, 1)[min_step[k]:]

            # print(data[k][trial])

            deriv2 = np.gradient(np.gradient(data[k][trial], 1), 1)[min_step[k]:]
            direct_deriv = savgol_filter(data[k][trial], widths[k], 3, mode='nearest', deriv=2)[min_step[k]:]

            min_deriv = np.argmin(direct_deriv) + min_step[k]
            max_deriv = np.argmax(direct_deriv) + min_step[k]

            debris_lengths[k].append(min_diff)
            droplet_lengths[k].append(max_deriv - min_diff)
            defect_lengths[k].append(min_deriv - max_deriv)

            if max_deriv - min_diff < 0 or min_deriv - max_deriv < 0:
                showing = True
            # print(trial)

            # if showing and trial % 32 == 12:
            #     if size == 128:
            #         yticks = [0, 4000, 8000, 12000, 16000]
            #     elif size == 256:
            #         yticks = [0, 15000, 30000, 45000, 60000]
            #     elif size == 512:
            #         yticks = [0, 50000, 100000, 150000, 200000, 250000, 300000]


            #     fig, axes = plt.subplots(nrows=2, figsize=(5, 3))
            #     plt.locator_params(nbins=5)       

            #     axes[0].plot(range(500), data[k][trial])
            #     axes[0].scatter(min_diff, np.min(data[k][trial]))
            #     axes[0].scatter(min_deriv, data[k][trial][min_deriv])
            #     axes[0].scatter(max_deriv, data[k][trial][max_deriv])
            #     axes[0].set_ylabel('$\Delta(t)$')
            #     axes[0].set_xlim(0, 500)
            #     axes[0].set_ylim(ymin=0)
            #     if size == 128:
            #         axes[0].set_ylim(ymax=17000)

            #     axes[1].plot(range(min_step[k], 500), deriv2, label='Raw derivative')
            #     axes[1].plot(range(min_step[k], 500), direct_deriv, color='black', label='Savitzky-Golay output')
            #     axes[1].set_ylabel("$\Delta''(t)$")
            #     axes[1].set_xlim(0, 500)


            #     axes[1].legend(loc='upper right', fontsize=8)
            #     axes[0].tick_params(axis='x', which='major', labelsize=8)
            #     axes[1].tick_params(axis='both', which='major', labelsize=8)
            #     plt.sca(axes[0])
            #     plt.yticks(yticks, yticks, fontsize=8)
            #     plt.sca(axes[1])

            #     plt.suptitle('$\Delta(t)$ curve ($k={}$, {} neighborhood)'.format(k, 'von Neumann' if vn else 'Moore'))
            #     plt.xlabel('Step ($t$)')
            #     plt.yticks(rotation='horizontal')
            #     # os.makedirs(cca_dir + 'plots/diff_curves/{}_{}/'.format(size, neighborhood), exist_ok=True)
            #     # plt.savefig(cca_dir + 'plots/diff_curves/{0}_{1}/{0}_{1}_k_{2}.pdf'.format(size, neighborhood, k), bbox_inches='tight')
            #     plt.show()
            #     plt.close()

        

    print('Pickling results...')
    with open(cca_dir + '/pickles/{}_{}.pkl'.format(size, neighborhood), 'wb') as f:
        pickle.dump([debris_lengths, droplet_lengths, defect_lengths], f)

if __name__ == '__main__':
    if sys.argv[1] == 'all':
        for neighborhood, size in itertools.product(['vn', 'moore'], [128, 256, 512]):
            main(neighborhood, size)
    else:
        main(sys.argv[1], int(sys.argv[2]))