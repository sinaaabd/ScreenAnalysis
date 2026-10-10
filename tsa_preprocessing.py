'''
    Create folders with the name same as csv files (raw data - Plate ID) if we have multiple or single experiments
    Author: Sina Abdollahi
    Date: 12.03.2025   
'''
import os
import pandas as pd
import shutil
import argparse


if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--main_dir_multiple', required=False, help='Directory containing all experiments.')
    parser.add_argument('--main_dir_single', required=False, help='Directory containing a single experiment.')
    parser.add_argument('--path_to_tsa_layout', required=True, help='The TSA_Layout.xlsx file path.')
    parser.add_argument('--output_path', required=True, help='The output folder path.')
    parser.add_argument('--extract_type', default='root_dir', help="Save in the root directory or save in different sub-directories", choices=['separate_dirs', 'root_dir'])
    args = parser.parse_args()
    
    if(args.main_dir_single and args.main_dir_multiple):
        print("Please only use either main_dir_multiple or main_dir_single")
        exit(0)
    if(not(args.main_dir_single or args.main_dir_multiple)):
        print("Please use at least one of the following options: main_dir_multiple, main_dir_single")
        exit(0)
        
    src_tsa_layout = args.path_to_tsa_layout
    if(args.main_dir_multiple):
        # For example: '340K_Screen/RawData and Log Files/ThermalShiftAssay'
        main_dir = args.main_dir_multiple
        for folder in os.listdir(main_dir):
            if(folder == '.DS_Store'):
                continue
            path = f'{main_dir}/{folder}'
            for raw_data_file in os.listdir(path):
                split_s = raw_data_file.split('-')
                if((raw_data_file.find('.csv') != -1) and ((raw_data_file.find('TSA-Template') != -1) or ((len(split_s) == 2) and (len(split_s[0]) == 7 or len(split_s[0]) == 8)))):
                    is_passed = True
                    if(raw_data_file.find('TSA-Template') != -1):
                        raw_df = pd.read_csv(f'{path}/{raw_data_file}', sep=";", encoding="latin1")
                        plate_id = list(raw_df[raw_df['Cy5']=='Title:']['SampleID'])[0]
                    elif(len(split_s[1]) == 3):
                        plate_id = raw_data_file.split('.csv')[0]
                    else:
                        is_passed = False
                    if(is_passed):
                        the_path = f'{args.output_path}/{folder}'
                        if(args.extract_type == 'root_dir'):
                            the_path = args.output_path
                        os.makedirs(f'{the_path}/{plate_id}', exist_ok=True)
                        shutil.copy(f'{path}/{raw_data_file}', f'{the_path}/{plate_id}/TSA_RawData.csv')
                        shutil.copy(src_tsa_layout, f'{the_path}/{plate_id}/TSA_Layout.xlsx')
    if(args.main_dir_single):
        # For example: 'RawData'
        path = args.main_dir_single
        for raw_data_file in os.listdir(path):
            if(raw_data_file.find('.csv') != -1):
                if(raw_data_file.find('TSA-Template') != -1):
                    raw_df = pd.read_csv(f'{path}/{raw_data_file}', sep=";", encoding="latin1")
                    plate_id = list(raw_df[raw_df['Cy5']=='Title:']['SampleID'])[0]
                else:
                    plate_id = raw_data_file.split('.csv')[0]
                the_path = args.output_path
                os.makedirs(f'{the_path}/{plate_id}', exist_ok=True)
                shutil.copy(f'{path}/{raw_data_file}', f'{the_path}/{plate_id}/TSA_RawData.csv')
                shutil.copy(src_tsa_layout, f'{the_path}/{plate_id}/TSA_Layout.xlsx')
