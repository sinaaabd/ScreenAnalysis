'''
    Add the Thermal Shift Assay information to the main Excel File containing all information about the experiments
    Author: Sina Abdollahi
    Date: 12.03.2025    
'''
from openpyxl.utils import column_index_from_string
from openpyxl import load_workbook
import pandas as pd
import string
import os
import argparse

if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_tsa', required=True, help='Directory containing all Thermal Shift Assay folders labeled as Plate IDs')
    parser.add_argument('--path_to_main_excel', required=True, help='The path and the name of the main Excel file')
    parser.add_argument('--output_file', required=False, help='The output Excel file path and name (by default we overwrite the results on the main Excel file)')
    parser.add_argument('--well_col', help='Declare the column name of the Wells', default='compound')
    parser.add_argument('--tm_col', help='Declare the column name of the Tm values', default='tm2_1')
    parser.add_argument('--fl25_col', help='Declare the column name of the fl25 values', default='fl25_1')
    parser.add_argument('--tsa_filename', help='Declare the name of the TSA CSV files', default='result.csv')
    args = parser.parse_args()
    
    if(args.output_file):
        output_file_path = args.output_file
    else:
        output_file_path = args.path_to_main_excel

    #For example:  "Thermal_Shift_Assays"
    path = args.path_to_tsa
    tsa_filename = args.tsa_filename
    well_col = args.well_col
    tm_col = args.tm_col
    fl25_col = args.fl25_col
    #For example: 'PO-ini2810.xlsx'    
    main_file_path = args.path_to_main_excel
    stsa_df = pd.read_excel(main_file_path, engine="openpyxl")
    available_wells = list(stsa_df['Well'].unique())

    thermal_shift_values_dictionary = {}
    fluorescence_at_25_values_dictionary = {}
    for folder in os.listdir(path):
        if((folder.find('.')==-1) and ((folder.find('-') != -1) or (len(folder) <= 5))):
            plate_id = folder
            tsa_df = pd.read_csv(f'{path}/{folder}/{tsa_filename}')
            tsa_df = tsa_df[[well_col, tm_col, fl25_col]]
            tsa_df = tsa_df[tsa_df[well_col].isin(available_wells)]
            thermal_shift_values_dictionary[plate_id] = tsa_df.set_index(well_col)[tm_col].to_dict()
            fluorescence_at_25_values_dictionary[plate_id] = tsa_df.set_index(well_col)[fl25_col].to_dict()
            os.system(f'echo {plate_id} >> tsa.log')

    def map_tsa_values(row):
        return thermal_shift_values_dictionary.get(row['Plate_ID'], {}).get(row['Well'], None)
    def map_fl25_values(row):
        return fluorescence_at_25_values_dictionary.get(row['Plate_ID'], {}).get(row['Well'], None)

    stsa_df['Thermal_Shift'] = stsa_df.apply(map_tsa_values, axis=1)
    stsa_df['Fluorescence_at_25'] = stsa_df.apply(map_fl25_values, axis=1)
    stsa_df.to_excel(output_file_path, index=False)
