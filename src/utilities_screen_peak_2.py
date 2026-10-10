import os
import numpy as np
import pandas as pd
import string
import json
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, differential_evolution
from scipy.interpolate import CubicSpline
from scipy.signal import find_peaks
from src.gmm_2 import *


def layout2dict(layout, save_dir=None):

    # Organize data in dictionary
    # We will make a tree-like structure "protein -> compound -> dosage" that contains well positions as a dictionary
    # well_positions_dict[protein][compound][dosage]
    # protein = NPC    means no protein
    # compound = NCC   means no compound
    # dosage = NCC     means no compound = 0 µM
    
    ## creates a list of all unique names
    unique_names = pd.unique(layout.values.ravel())
    
    ## Get all proteins, dosages, and compounds
    protein = [i.split(' ')[0] for i in unique_names if isinstance(i, str)] # remove NaN, get first element (protein variant)
    dosage = [i.split(' ')[1] for i in unique_names if isinstance(i, str)]  # remove NaN, get 2nd element (protein variant)
    compound = [i.split(' ')[2] if len(i.split(' ')) == 3 else 'NCC' for i in unique_names if isinstance(i, str) ] # remove NaN, get 3rd element (protein variant)
    
    ## define dictionary and fill the dictionary
    def find_in_layout(layout, name):
        pos = []
        for row in range(layout.shape[0]):
            for col in range(layout.shape[1]):
                if layout.iat[row, col] == name:
                    # Convert column/line numbers to formate A1-P24
                    row_label = string.ascii_uppercase[row]
                    col_label = col + 1
                    pos.append((row_label, col_label))
        return pos
    
    dict = {k:{} for k in protein}            # k means key
    for p in dict.keys():                     # p means protein
        dict[p] = {k:{} for k in compound}
        for c in dict[p].keys():              # c means compound  
            if c == 'NCC':
                    name = p + ' ' + c
                    dict[p][c] = find_in_layout(layout, name)
            else:
                dict[p][c] = {k:{} for k in dosage if k != 'NCC'}
                for d in dict[p][c].keys():         # d means dosage
                    name = p + ' ' + d + ' ' + c
                    dict[p][c][d] = find_in_layout(layout, name)
    
    well_positions_dict = dict

    if save_dir is not None:
        with open(os.path.join(save_dir, "well_positions_dict.json"), 'w') as file:
            json.dump(well_positions_dict, file)

    return well_positions_dict

def assym_sigmoid(x, b, c, d, e, f):
    return (c + ( (d - c) / (1 + np.exp(b * (np.log(x) - np.log(e))))**f ))


def midpointTm(b, e, f, minmax=None, eps=1e-6):
    if minmax != None:
        min, max = minmax
    tm = e / np.exp(-np.log(2**(1/f) - 1) / b)
    return tm if minmax==None else (tm + eps) * (max - min) + min


def curve_fitting(x, y):
    eps = 1e-6

    # Normalise time
    t_min = x.min()
    t_max = x.max()
    x = (x - t_min) / (t_max - t_min) + eps
    x = list(x)
    y = list(y)

    # Perform curve fitting
    for max_f in [10, 100, 1000, 10000]:                       # max_f may need to vary depending on the input data
        initial_guess = (10, 1, 50, 10, 10)
        bounds = ([eps, eps, eps, eps, .1],                      # Lower bounds
                  [100, 100, 100, 100, max_f])                   # Upper bounds

        try:
            popt, pcov = curve_fit(assym_sigmoid, (x), y, p0=initial_guess, bounds=bounds)
            b, c, d, e, f = tuple(popt)                                         
        except:
            b, c, d, e, f = (1, 1, 1, 1, 1)
            continue
    
        # get y_hat and midpointTm
        y_hat = assym_sigmoid(x, b, c, d, e, f)
        midTm = midpointTm(b, e, f, (t_min, t_max))
    
        # Calculate R^2
        ss_res = np.sum((y - y_hat) ** 2)       # Residual sum of squares
        ss_tot = np.sum((y - np.mean(y)) ** 2)  # Total sum of squares
        r_squared = 1 - (ss_res / ss_tot)
        if r_squared > 0.5:
            break

    return y_hat, midTm, r_squared


def curve_fitting2(x, y):

    eps = 1e-6
    def objective_function(params, x, y):
        return np.sum((y - assym_sigmoid(x, *params))**2)

    # Normalise time
    t_min = x.min()
    t_max = x.max()
    x = (x - t_min) / (t_max - t_min) + eps
    x = list(x)
    y = list(y)

    # Perform curve fitting
    for max_f in [100, 1000]:                       # max_f may need to vary depending on the input data
        bounds = [(eps, 10), (eps, 10), (eps, 10), (eps, 10), (1, max_f)]

        result = differential_evolution(objective_function, bounds, args=(x, y), strategy='best1bin', maxiter=1000)
        popt = result.x
        b, c, d, e, f = tuple(popt) 
    
        # get y_hat and midpointTm
        y_hat = assym_sigmoid(x, b, c, d, e, f)
        midTm = midpointTm(b, e, f, (t_min, t_max))
    
        # Calculate R^2
        ss_res = np.sum((y - y_hat) ** 2)       # Residual sum of squares
        ss_tot = np.sum((y - np.mean(y)) ** 2)  # Total sum of squares
        r_squared = 1 - (ss_res / ss_tot)
        if r_squared > 0.5:
            break

    return y_hat, midTm, r_squared

def cut_curve(y, rtn_drv = False):
    # find maximum point from right, and turning point from left
    def D(x):
        x = np.array(x)
        return x[1:len(x)] - x[0:len(x)-1]
    
    d_y = D(y)
    d2_y = D(d_y)
    d3_y = D(d2_y)

    # 1. Find the steepest slop as for the center
    center = np.argmax(d_y)

    # 2. Move to right to reach the maximum
    for i in np.arange(center, len(y)-1, 1):
        if y[i+1] < y[i]:
            break
    cut_max = i

    # 3. Move to left to get to the min of y'
    for i in np.arange(center, 1, -1):
        if (d_y[i-1] > d_y[i]) or (d_y[i-1] * d_y[i] < 0):
            break
    cut_min = i
    
    if rtn_drv:
        return cut_min, cut_max, center, d_y, d2_y
    else:
        return cut_min, cut_max, center


def get_melting_tempreture_peak(x, y, fit_curve = True, min_temp_peak=37, max_temp_peak=58, method = "cut", window = 50):

    """
    This is a parallell version of the function
    get_melting_tempreture()
    that considers tm as the peak temp
    """

    y = np.array(list(y))
    x = np.array(list(x))
    
    ind_peak = find_peaks(y, distance=5)[0]
    # valid_peaks = [i for i in ind_peak if x[i] >= min_temp_peak]
    valid_peaks = [i for i in ind_peak if min_temp_peak <= x[i] <= max_temp_peak]

    peak_count = len(valid_peaks)

    y_peak = y[valid_peaks]
    x_peak = x[valid_peaks]

    if valid_peaks:
        peak_max_ind = np.argmax(y_peak)
        Tm_peak = x_peak[peak_max_ind]
    else:
        Tm_peak = None

    # for i in ind_peak:
    #     if x[i] >= min_temp_peak:
    #         Tm_peak = x[i]
    #         break

    
    # cut_min, cut_max, center = cut_curve(y)

    # if method == "pad":
    #     cut_min_new = cut_min - window
    #     cut_max_new = cut_max + window
    #     if cut_min_new <= 0:
    #         cut_min_new = 0
    #     if cut_max_new >= len(y):
    #         cut_max_new = len(y)
    
    #     y_max = y[cut_max]
    #     y_min = y[cut_min]
    
    #     y[cut_max + 1 : len(y)] = y[cut_max]
    #     y[0 : cut_min - 1] = y[cut_min]

    # # Cut curve
    # elif method == "cut":
    #     x = x[cut_min : cut_max]
    #     y = y[cut_min : cut_max]

    # # Do the main curve fitting
    # if fit_curve:
    #     y_hat, midTm_cf, r_squared = curve_fitting2(x, y)
    # else:
    #     y_hat, midTm_cf, r_squared = (0, 0, 0)

    y_hat = y
    
    return peak_count, Tm_peak, x, y, y_hat, x_peak


def cubic_spline(x, y, n):
    cs = CubicSpline(x, y)
    x_new = np.linspace(min(x), max(x), n)
    y_new = cs(x_new)
    return pd.Series(x_new), pd.Series(y_new)


def remove_header(file_path, sep=','):

    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        file_new = []
        key_flag = 0
        for i, line in enumerate(file):
            key = line.split(sep)[0] 
            if key == "SyproOrange" or key=="Cy5":
                key_flag = 1
            if key_flag == 1:
                file_new.append(line)

    file_path_new = file_path.split('.')
    file_path_new = file_path_new[0] + '_removed_header.csv'
    with open(file_path_new, 'w') as file:
        for line in file_new:
            file.write(line)


def read_tsa_rawdata(working_dir, return_type=False):
    # Read the raw data
    file_type = 0
    remove_header(os.path.join(working_dir,'TSA_RawData.csv'))
    try:    # type I data with header being removed
        rawdata = pd.read_csv(os.path.join(working_dir,'TSA_RawData_removed_header.csv'), index_col=0, encoding='ISO-8859-1')
        file_type = 1
    except: # type II data with ; as separator and extra rows to be removed
        try:
            rawdata = pd.read_csv(os.path.join(working_dir,'TSA_RawData.csv'), encoding='ISO-8859-1', sep=';', index_col = 0)
            rawdata = rawdata.apply(pd.to_numeric, errors='coerce')
            rawdata = rawdata.drop(['SampleID'], axis=1)
            pattern = '^[A-Z][0-9]{1,2}$'
            to_keep = [bool(re.findall(pattern, str(i))) for i in rawdata.index]
            rawdata = rawdata.loc[to_keep]
            file_type = 2
        except: # type III data with ; as separator and headers
            remove_header(os.path.join(working_dir,'TSA_RawData.csv'), sep=';')
            rawdata = pd.read_csv(os.path.join(working_dir,'TSA_RawData_removed_header.csv'), index_col=0, encoding='ISO-8859-1', sep=';')
            rawdata = rawdata.apply(pd.to_numeric, errors='coerce')
            file_type = 3

    if return_type:
        try:
            os.remove(os.path.join(working_dir,'TSA_RawData_removed_header.csv'))
        except:
            pass
        return file_type
    else:
        return rawdata




def process2(well_positions_dict, rawdata, protein, compound, dosage='None', save_dir='./', max_replicate=4,
             protein_ctrl = 'NPC', compound_ctrl = 'NCC',
             smoothing_window = 5, smoothing_repeats = 2, fit_curve = True,
             plt_raw = True, plt_smoothed = True, plt_final_curve = True,     # all plots
             return_smoothed = True):


    """
    This process2 is adopted for screening data.
    - The rawdata is row-wise
    - There is no NPC (protein control) and NCC (compound control)[?]
    - The number of replicates is flexible
    """
    
    # print(f'Processing {protein}, {compound}, {dosage}')
    # Make save_dir
    save_dir_fig_other = os.path.join(save_dir, 'fig_other')
    save_dir_fig_final = os.path.join(save_dir, 'fig_final')
    if not os.path.exists(save_dir_fig_other):
        os.makedirs(save_dir_fig_other)
    if not os.path.exists(save_dir_fig_final):
        os.makedirs(save_dir_fig_final)

    # Select the desired assay   
    well_positions_target = well_positions_dict[protein][compound][dosage] if compound != compound_ctrl else well_positions_dict[protein][compound]                       #non NCC values
    n_replicate = len(well_positions_target)
    # print(n_replicate)
    n_fig = int((n_replicate+1) / 2)
    
    # Get Fluorescence for target well positions
    well_positions_target_ = [a + str(b) for a, b in well_positions_target]
    df = rawdata.loc[well_positions_target_].T                                         ########### - #########
    df.insert(0, "Temperature", df.index)
    df['Temperature'] = df['Temperature'].astype(float)
    
    # Raw figures
    if plt_raw:
        fig, axes = plt.subplots(n_fig, 2, figsize=(10, 8))
        axes = axes.flatten()
        for i in range(1,n_replicate+1):
            axes[i-1].plot(df['Temperature'], df.iloc[:,i])
        plt.savefig(os.path.join(save_dir_fig_other, '_'.join([protein, compound, dosage]) + '_raw.jpeg'))
        plt.close(fig)

    ## absolute fluorescence at 25 deg
    fl25 = np.array(df.iloc[0, 1:])

    # Apply moving average
    for i in range(1,n_replicate+1):
        for r in range(smoothing_repeats):
            df.iloc[:,i] = df.iloc[:,i].rolling(window=smoothing_window, center=True).mean()
            df.iloc[:,i] = df.iloc[:,i].fillna(method='bfill').fillna(method='ffill')

    # Smoothed figures
    if plt_smoothed:
        fig, axes = plt.subplots(n_fig, 2, figsize=(10, 8))
        axes = axes.flatten()
        for i in range(1,n_replicate+1):
            axes[i-1].plot(df['Temperature'], df.iloc[:,i], linewidth=2)
        plt.savefig(os.path.join(save_dir_fig_other, '_'.join([protein, compound, dosage]) + '_smoothed.jpeg'))
        plt.close(fig)
    
    # Normalization    
    for i in range(1,n_replicate+1):
        df.iloc[:,i] = (df.iloc[:,i] - df.iloc[:,i].min()) / (df.iloc[:,i].max() - df.iloc[:,i].min())               # min-max normalization
    if return_smoothed:
        df_smoothed = df.copy()   # keep this to return

    # Get melting tempreture with and without curve fitting
    curve_info = {}
    for i in range(1,n_replicate+1):
        t = df['Temperature']
        y = df.iloc[:,i]
        # t, y = cubic_spline(t, y, n=500)
        # midTm2, midTm, t, y, y_hat, valid_peaks = get_melting_tempreture_peak(t, y, fit_curve=fit_curve)
        # y_hat, midTm, r_squared = curve_fitting2(t, y)
        
        t, y_, y, mu1, mu2, rmse = gaussian_mixture_smooth_2(t, y)
        midTm2, midTm, t, y, y_hat, valid_peaks = 2, mu1, t, y, y, [mu1, mu2]

        # rmse = 0
        
        curve_info[i] = {}
        curve_info[i]['y'] = y
        curve_info[i]['y_hat'] = y_hat
        curve_info[i]['t'] = t
        curve_info[i]['midTm'] = midTm
        curve_info[i]['r_squared'] = rmse
        curve_info[i]['midTm2'] = midTm2
        curve_info[i]['valid_peaks'] = valid_peaks

    if plt_final_curve:
        fig, axes = plt.subplots(n_fig, 2, figsize=(10, 8))
        axes = axes.flatten()
        for i in range(1,n_replicate+1):            
            axes[i-1].plot(curve_info[i]['t'], curve_info[i]['y'], linewidth=2)
            axes[i-1].vlines(curve_info[i]['valid_peaks'], ymin = 0, ymax = 1, linewidth=1, colors='red')    
            if fit_curve:
                axes[i-1].plot(curve_info[i]['t'], curve_info[i]['y_hat'], linewidth=2)            
        plt.savefig(os.path.join(save_dir_fig_final, '_'.join([protein, compound, dosage]) + '.jpeg'))
        plt.close(fig)

    ## tm_average and tm_std
    tm_list = [curve_info[i]['valid_peaks'][0] for i in range(1,n_replicate+1)]
    tm_mean = np.mean(tm_list)
    tm_std = np.std(tm_list)
    tm_list = np.append(tm_list, [np.nan] * (max_replicate - n_replicate)) # Add "na" values to tm_list if their length is smaller than max_replicate
    tm_list = np.append(tm_list, tm_mean)
    tm_list = np.append(tm_list, tm_std)
    tm_list = tm_list.round(4)

    ## tm_average2 and tm_std2
    tm_list2 = [curve_info[i]['valid_peaks'][1] for i in range(1,n_replicate+1)]
    tm_mean2 = np.mean(tm_list2)
    tm_std2 = np.std(tm_list2)
    tm_list2 = np.append(tm_list2, [np.nan] * (max_replicate - n_replicate)) # Add "na" values to tm_list if their length is smaller than max_replicate
    tm_list2 = np.append(tm_list2, tm_mean2)
    tm_list2 = np.append(tm_list2, tm_std2)
    tm_list2 = tm_list2.round(4)    

    ## r_squared
    r_squared_list = np.array([curve_info[i]['r_squared'] for i in range(1,n_replicate+1)])
    r_squared_list = r_squared_list.round(4)
    r_squared_list = np.append(r_squared_list, [np.nan] * (max_replicate - n_replicate)) # Add "na" values to tm_list if their length is smaller than max_replicate
    
    out = (
        [protein,
         compound, 
         dosage,
         '-'.join([a + str(b) for a, b in well_positions_target]),
        ] + 
        [str(i) for i in tm_list] + 
        [str(i) for i in tm_list2] + 
        [str(i) for i in r_squared_list] + 
        [str(i) for i in fl25]
    )
    
    return (out, df_smoothed) if return_smoothed else out
