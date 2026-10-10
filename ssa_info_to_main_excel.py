'''
    Add the Sepctral Shift Assay information to the main Excel File containing all information about the experiments
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
    parser.add_argument('--path_to_ssa', required=True, help='Directory containing all Spectral Shift Assay CSV files with plate ID as their name.')
    parser.add_argument('--path_to_main_excel', required=True, help='The path and the name of the PO Excel file')
    parser.add_argument('--output_file', required=False, help='The output PO Excel file path and name (by default we overwrite the results on the main Excel file)')
    args = parser.parse_args()
    
    if(args.output_file):
        output_file_path = args.output_file
    else:
        output_file_path = args.path_to_main_excel
    
    #For example: 'PO-ini2810.xlsx'    
    main_file_path = args.path_to_main_excel
    ssa_df = pd.read_excel(main_file_path, engine="openpyxl")
    buffer_wells_list = [chr(i)+'01' for i in range(ord('G'), ord('P') + 1)]

    #For example: 'Spectral_Shift_Assays'
    path = args.path_to_ssa
    spectral_shift_values_dictionary = {}
    for plate_id in os.listdir(path):
        if(plate_id == '.DS_Store'):
            continue
        if((plate_id.find('-')!= -1) or (len(plate_id) <= 5)):
            spectral_shift_values_dictionary[plate_id] = {}

            first_df = pd.read_csv(f'{path}/{plate_id}/SSA_RawData.csv', header=None)
            first_df.columns = range(1, len(first_df.columns) + 1)

            first_df = first_df.dropna(how='all')

            second_df = first_df.iloc[16:]
            second_df.index = list(string.ascii_uppercase[:len(second_df)])
            first_df = first_df.iloc[:16]
            first_df.index = list(string.ascii_uppercase[:len(first_df)])

            first_avg = first_df[1][6:].mean()
            second_avg = second_df[1][6:].mean()

            final_df = (first_df-first_avg)/(second_df-second_avg)

            for row in list(final_df.index):
                for col in range(1, len(final_df.columns)+1):
                    spectral_value = final_df.loc[row,col]
                    well_id = f'{row}{col}'
                    if(col < 10):
                        well_id = f'{row}0{col}' 
                    if(well_id not in buffer_wells_list):
                        spectral_shift_values_dictionary[plate_id][well_id] = spectral_value

            os.system(f'echo {plate_id} >> spsh.log')
        else:
            print("There is a folder which is not in a correct format! Missing '-' in the plate ID.")

    def map_values(row):
        return spectral_shift_values_dictionary.get(row['Plate_ID'], {}).get(row['Well'], None)

    ssa_df['Spectral_Shift'] = ssa_df.apply(map_values, axis=1) 
    ssa_df.to_excel(output_file_path, index=False)
