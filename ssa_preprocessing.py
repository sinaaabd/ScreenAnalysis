'''
    Create folders with the name same as csv files (raw data - Plate ID) when we have multiple experiments
    Author: Sina Abdollahi
    Date: 18.03.2025   
'''
import os
import pandas as pd
import shutil
import argparse
import pickle


if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--main_dir', required=True, help='Directory containing all SpSh experiments.')
    parser.add_argument('--output_path', required=True, help='The output folder path.')
    args = parser.parse_args()
    
    spsh_plate_id_to_file_mapper = {}
    if(os.path.exists('SpSh_Conversion_Table.pickle')):
        spsh_plate_id_to_file_mapper = pickle.load(open('SpSh_Conversion_Table.pickle', 'rb'))
    main_dir = args.main_dir
    for folder in os.listdir(main_dir):
        if(folder == '.DS_Store'):
            continue
        src_path = f'{main_dir}/{folder}'
        for raw_data_file in os.listdir(src_path):
            if(raw_data_file.find('.csv') != -1):
                plate_id = raw_data_file.split('.csv')[0]
                if((plate_id.find('-')==-1) and (len(plate_id) > 5)):
                    plate_id = f'{plate_id[:-3]}-{plate_id[-3:]}'
                if(plate_id not in spsh_plate_id_to_file_mapper):
                    spsh_plate_id_to_file_mapper[plate_id] = raw_data_file
                os.makedirs(f'{args.output_path}/{plate_id}', exist_ok=True)
                shutil.copy(f'{src_path}/{raw_data_file}', f'{args.output_path}/{plate_id}/SSA_RawData.csv')
    pickle.dump(spsh_plate_id_to_file_mapper, open('SpSh_Conversion_Table.pickle', 'wb'))
