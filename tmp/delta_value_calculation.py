"""
    Calculating DeltaTm and DeltaSpSh
    Version 0.1.0
    Authors:
        - Nora Constanze Laubach (laubach@iniuva.com)
        - Behnam Yousefi (behnm.yousefi@zmnh.uni-hamburg.de; yousefi.bme@gmail.com)
    UKE, Hamburg, Germany - Apr 2025
"""

import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import argparse
from src.utilities_analysis import *
import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    
    # Read inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--PO_table_path', required=True, help='Path to the PO table.')
    
    args = parser.parse_args()
    PO_table_path = args.PO_table_path

    # Read PO table
    print(f'Reading the PO table at {PO_table_path}')
    df = pd.read_excel(PO_table_path)

    # get the df of DMSO as the negative control
    df_DMSO = df.loc[df['ID'] == 'DMSO']
    uniq_Plate_IDs = df_DMSO['Plate_ID'].unique()

    
    # Create df_tsa_ctrl
    # each row corresponds a plate
    # cols: tsa/spsh + statistics
    print('Creating table of controls for TSA')
    
    columns_table = (
        ['Plate_ID', 'Protein', 'Compound'] + 
        [f'Rep{i}' for i in range(1, 17)] + 
        ['Median', 'IQR', 'IQR_rel[%]', 'Mean', 'STD']
    )
    df_tsa_ctrl = pd.DataFrame(columns = columns_table)    #creates empty table with specified columns
    
    ## Loop over uniq_Plate_IDs
    for i in tqdm(range(len(uniq_Plate_IDs))):
        
        plate_ID = uniq_Plate_IDs[i]
        protein = df.loc[df['Plate_ID'] == plate_ID, 'Protein'].unique().item()
        compound = 'DMSO'
    
        # Get control values for TSA
        df_temp = df.loc[(df['ID'] == compound) & (df['Plate_ID'] == plate_ID)].copy()    
        # ^^^ creates a subset of df, where additionally only one Plate ID is shown  ()&()
        
        df_temp = df_temp.dropna(subset = ['Thermal_Shift'])   # discards all lines where Thermal Shift is NaN
        
        tm = df_temp['Thermal_Shift'].tolist()     # creates a one column table and then converts to list
        if len(tm):
            stats = statistics(tm)
            newline = [plate_ID, protein, compound] + tm + list(stats.values())     
            df_tsa_ctrl.loc[len(df_tsa_ctrl)] = newline          
            # hint: len(df) above is number of existing lines; here, "newline" is added at the end of the table

    # Create df_spsh_ctrl
    # each row corresponds a plate
    # cols: tsa/spsh + statistics
    print('Creating table of controls for SpSh')
    
    columns_table = (
        ['Plate_ID', 'Protein', 'Compound'] + 
        [f'Rep{i}' for i in range(1, 17)] + 
        ['Median', 'IQR', 'IQR_rel[%]', 'Mean', 'STD']
    )
    df_spsh_ctrl = pd.DataFrame(columns = columns_table)
    
    # Loop over uniq_Plate_IDs
    for i in tqdm(range(len(uniq_Plate_IDs))):
        
        plate_ID = uniq_Plate_IDs[i]
        protein = df.loc[df['Plate_ID'] == plate_ID, 'Protein'].unique().item()
        compound = 'DMSO'
    
        # Get control values for TSA
        df_temp = df.loc[(df['ID'] == compound) & (df['Plate_ID'] == plate_ID)].copy()
        df_temp = df_temp.dropna(subset = ['Spectral_Shift'])                              
        
        tm = df_temp['Spectral_Shift'].tolist()
        if len(tm):
            stats = statistics(tm)
            newline = [plate_ID, protein, compound] + tm + list(stats.values())     
            df_spsh_ctrl.loc[len(df_spsh_ctrl)] = newline
    
    # Calculate delta_Tm
    # Produce warnings
    # Add entities to the PO table
    print('Calculate delta_Tm and add to the PO table')
    
    df['delta_Tm_median'] = None
    df['delta_Tm_mean'] = None
    df['Tm_Warning'] = None
    
    for i in tqdm(range(len(df))):
    
        Thermal_Shift = df.loc[i, 'Thermal_Shift']
        Plate_ID = df.loc[i, 'Plate_ID']
    
        df_tmp = df_tsa_ctrl.loc[df_tsa_ctrl['Plate_ID'] == Plate_ID]
        Median_DMSO = df_tmp['Median']
        Mean_DMSO = df_tmp['Mean']
        IQR_rel_DMSO = df_tmp['IQR_rel[%]']
        
        if Median_DMSO.empty or Mean_DMSO.empty:
            continue
            
        deltaTm_median = Thermal_Shift - Median_DMSO
        deltaTm_mean = Thermal_Shift - Mean_DMSO
    
        df.loc[i, 'delta_Tm_median'] = deltaTm_median.item()
        df.loc[i, 'delta_Tm_mean'] = deltaTm_mean.item()  
    
        # Make warnings
        warning = ''
        if IQR_rel_DMSO.item() >1:
            warning = warning + ' Warning: high Tm IQR for DMSO controls!'
        if Median_DMSO.item() <48.7:           ######### THIS VALUE IS ONLY TRUE FOR PAH WT !!!!!    
            warning = warning + ' Warning: low Tm for DMSO controls!'
        df.loc[i, 'Tm_Warning'] = warning

    # Calculate delta_SpSh
    # Produce warnings
    # Add entities to the PO table
    print('Calculate delta_SpSh and add to the PO table')
    
    df['delta_SpSh_median'] = None
    df['delta_SpSh_mean'] = None
    df['SpSh_Warning'] = None
    
    for i in tqdm(range(len(df))):
    
        Spectral_Shift = df.loc[i, 'Spectral_Shift']
        Plate_ID = df.loc[i, 'Plate_ID']
    
        df_tmp = df_spsh_ctrl.loc[df_spsh_ctrl['Plate_ID'] == Plate_ID]
        Median_DMSO = df_tmp['Median']
        Mean_DMSO = df_tmp['Mean']
        IQR_rel_DMSO = df_tmp['IQR_rel[%]']
        
        if Median_DMSO.empty or Mean_DMSO.empty:
            continue
            
        deltaS_median = Spectral_Shift - Median_DMSO
        deltaS_mean = Spectral_Shift - Mean_DMSO
    
        df.loc[i, 'delta_SpSh_median'] = deltaS_median.item()
        df.loc[i, 'delta_SpSh_mean'] = deltaS_mean.item()  
    
        # Make warnings
        warning = ''
        if IQR_rel_DMSO.item() > 1.2:             #### Behnam & Conny find better threshold together
            warning = warning + ' Warning: high SpSh IQR for DMSO controls!'
        df.loc[i, 'SpSh_Warning'] = warning


    print('Updating the PO table')
    df.to_excel(PO_table_path)
    print('Done! Now you are ready to do big things :)')
