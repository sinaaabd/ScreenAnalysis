"""
    Thermal shift assay analysis: screen version
    This code is modified only for the screen analysis
    Version 0.2.0
    Authors:
        - Nora Constanze Laubach (laubach@iniuva.com)
        - Behnam Yousefi (behnm.yousefi@zmnh.uni-hamburg.de; yousefi.bme@gmail.com)
    UKE, Hamburg, Germany - Jan 2025
"""

import os
import numpy as np
import pandas as pd
import json
import argparse
from tqdm import tqdm
import zipfile
import re
from src.utilities_screen import *
import warnings
warnings.filterwarnings("ignore")

protein_ctrl = 'NPC'
compound_ctrl = 'NCC'
fit_curve = False


if __name__ == "__main__":
    
    # Read inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--working_dir', required=True, help='Working directory for a single experiment.')

    args = parser.parse_args()
    working_dir = args.working_dir

    # read the layout file and convert it into the well_positions_dict
    layout = pd.read_excel(os.path.join(working_dir,'TSA_Layout.xlsx'), index_col=0)
    well_positions_dict = layout2dict(layout, working_dir)

    # Read the raw data
    remove_header(os.path.join(working_dir,'TSA_RawData.csv'))
    try:    # type I data with header being removed
        rawdata = pd.read_csv(os.path.join(working_dir,'TSA_RawData_removed_header.csv'), index_col=0, encoding='ISO-8859-1')
    except: # type II and IV data with ; as separator and extra rows to be removed
        try:
            rawdata = pd.read_csv(os.path.join(working_dir,'TSA_RawData.csv'), encoding='ISO-8859-1', sep=';', index_col = 0)
            rawdata = rawdata.drop(['SampleID'], axis=1)
            pattern = '^[A-Z][0-9]{1,2}$'
            to_keep = [bool(re.findall(pattern, str(i))) for i in rawdata.index]
            rawdata = rawdata.loc[to_keep]
            if len(rawdata.iloc[0,0].split(',')) == 1:       # II
                rawdata = rawdata.apply(pd.to_numeric, errors='coerce')
            else:                                            # IV
                rawdata = rawdata.apply(lambda x: x.str.replace(',', '.').astype(float))
                rawdata.columns = rawdata.columns.str.replace(',', '.')
        except: # type III data with ; as separator and headers
            remove_header(os.path.join(working_dir,'TSA_RawData.csv'), sep=';')
            rawdata = pd.read_csv(os.path.join(working_dir,'TSA_RawData_removed_header.csv'), index_col=0, encoding='ISO-8859-1', sep=';')
            rawdata = rawdata.apply(pd.to_numeric, errors='coerce')

    # Get all proteins, ligands and doses
    protein_set = list(well_positions_dict.keys())
    compound_set = list(well_positions_dict[protein_set[0]].keys())
    try:
        dosage_set = list(well_positions_dict[protein_set[0]][compound_set[0]].keys())
    except:
        dosage_set = list(well_positions_dict[protein_set[0]][compound_set[1]].keys())
    protein_set, compound_set, dosage_set

    # Get max_replicate
    max_replicate = 0
    for protein in protein_set:
        for compound in compound_set:
            for dosage in dosage_set:
                # try:
                well_positions_target = well_positions_dict[protein][compound][dosage] if compound != compound_ctrl else well_positions_dict[protein][compound]   
                # except:
                # well_positions_target = []
                if len(well_positions_target) > max_replicate:
                    max_replicate = len(well_positions_target)
            
    colnames = (['protein', 'compound', 'dosage', 'locations'] +
                [f'tm_{i}' for i in range(1, max_replicate+1)] + ['tm_mean', 'tm_std'] +
                [f'r_squared_{i}' for i in range(1, max_replicate+1)] +
                [f'tm2_{i}' for i in range(1, max_replicate+1)] + ['tm2_mean', 'tm2_std'] +
                [f'fl25_{i}' for i in range(1, max_replicate+1)]
           )
    df = pd.DataFrame(columns=colnames)
    
    curve = pd.DataFrame()
    
    # Loop over protein
    for protein in tqdm(protein_set):
        if protein == protein_ctrl:
            continue
        # Loop over compound
        for compound in compound_set:
            # check for 0 dosage
            if compound == compound_ctrl:
                row, crv = process2(well_positions_dict, rawdata,
                                    protein, compound,
                                    save_dir = working_dir,
                                    fit_curve = fit_curve,
                                    max_replicate = max_replicate)
                df.loc[len(df)] = row
                curve = pd.concat([curve, crv], axis=1)
            else:
                # Loop over dosage
                for dosage in dosage_set:
                    row, crv = process2(well_positions_dict, rawdata, 
                                        protein, compound, dosage, 
                                        save_dir = working_dir,
                                        fit_curve = fit_curve,
                                        max_replicate = max_replicate)
                    df.loc[len(df)] = row
                    curve = pd.concat([curve, crv], axis=1)
    
    curve.index = crv['Temperature']
    curve = curve.drop('Temperature', axis = 1)

    if not fit_curve:
        colnames = (['protein', 'compound', 'dosage', 'locations'] +
                    [f'tm2_{i}' for i in range(1, max_replicate+1)] + 
                    ['tm2_mean', 'tm2_std'] + 
                    [f'fl25_{i}' for i in range(1, max_replicate+1)]
                   )
        df = df[colnames]  
    
    # Save tables
    df.to_csv(os.path.join(working_dir, 'result.csv'))
    curve.to_csv(os.path.join(working_dir, 'curve.csv'))