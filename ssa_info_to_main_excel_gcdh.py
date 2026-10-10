'''
    Add the Sepctral Shift Assay information to the main Excel File containing all information about the experiments [GCDH version]
    Author: Sina Abdollahi
    Date: 23.05.2025  
    Last update: 19.06.2025
'''
import pandas as pd
import os
import argparse


if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_main_excel', required=True, help='The path and the name of the PO Excel file')
    parser.add_argument('--path_to_ssa', required=True, help='Directory containing all Spectral Shift Assay CSV files.')
    parser.add_argument('--output_file', required=False, help='The output PO Excel file path and name (by default we overwrite the results on the main Excel file)')
    args = parser.parse_args()
    
    path_to_raw_files = args.path_to_ssa
    path_to_PO_table = args.path_to_main_excel
    output_file_path = args.path_to_main_excel
    if(args.output_file):
        output_file_path = args.output_file
    
    PO_table = pd.read_excel(path_to_PO_table, engine="openpyxl")
    buffer_wells = ['A01', 'C01', 'E01', 'G01', 'I01', 'K01', 'M01', 'O01']
    for spsh_folder in os.listdir(path_to_raw_files):
        if(spsh_folder.find('.') == -1):
            plate_id = spsh_folder
            rawfile_df = pd.read_csv(f'{path_to_raw_files}/{spsh_folder}/SSA_RawData.csv')

            split_index = rawfile_df[rawfile_df['Time [s]: 0'].str.strip() == 'Time [s]: 0'].index[0]
            # Split into two DataFrames
            first_part_df = rawfile_df.iloc[:split_index].reset_index(drop=True)
            split_cols = first_part_df["Time [s]: 0"].str.replace(":", "").str.split(expand=True)
            first_part_df[["Plate_ID", "Well", "value"]] = split_cols
            first_part_df["value"] = pd.to_numeric(first_part_df["value"], errors='coerce')
            first_part_df = first_part_df[['Plate_ID', 'Well', 'value']]
            buffer_mean_first_part = first_part_df[first_part_df['Well'].isin(buffer_wells)]['value'].mean()

            second_part_df = rawfile_df.iloc[split_index + 1:].reset_index(drop=True)
            split_cols = second_part_df["Time [s]: 0"].str.replace(":", "").str.split(expand=True)
            second_part_df[["Plate_ID", "Well", "value"]] = split_cols
            second_part_df["value"] = pd.to_numeric(second_part_df["value"], errors='coerce')
            second_part_df = second_part_df[['Plate_ID', 'Well', 'value']]
            buffer_mean_second_part = second_part_df[second_part_df['Well'].isin(buffer_wells)]['value'].mean()

            result_series = (
                (first_part_df['value'] - buffer_mean_first_part) /
                (second_part_df['value'] - buffer_mean_second_part)
            )

            result_df = first_part_df.copy()
            result_df['Spectral_Shift'] = result_series
            result_df = result_df[['Plate_ID', 'Well', 'Spectral_Shift']]
            if('Spectral_Shift' not in PO_table.columns):
                PO_table['Spectral_Shift'] = pd.NA
            merged = PO_table.merge(
                result_df,
                on=['Plate_ID', 'Well'],
                how='left',
                suffixes=('', '_new')
            )
            merged['Spectral_Shift'] = merged['Spectral_Shift_new'].combine_first(merged['Spectral_Shift'])
            merged.drop(columns=['Spectral_Shift_new'], inplace=True)
            PO_table = merged
            print(plate_id)
    PO_table.to_excel(output_file_path, index=False)
