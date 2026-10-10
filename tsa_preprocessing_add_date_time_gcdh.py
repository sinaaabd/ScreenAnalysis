'''
    Create folders with the name same as csv files (raw data - Plate ID) if we have multiple or single experiments
    Author: Sina Abdollahi
    Date: 19.06.2025   
'''
import os
import pandas as pd
import shutil
import argparse
import csv
import pickle


if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--main_dir_multiple', required=True, help='Directory containing all experiments.')
    parser.add_argument('--path_to_tsa_layout', required=True, help='The TSA_Layout.xlsx file path.')
    parser.add_argument('--path_to_PO_file', required=True, help='The PO xlsx file path.')
    parser.add_argument('--output_path', required=True, help='The output folder path.')
    parser.add_argument('--extract_type', default='root_dir', help="Save in the root directory or save in different sub-directories", choices=['separate_dirs', 'root_dir'])
    args = parser.parse_args()
    
    tsa_plate_id_to_file_mapper = {}
    if(os.path.exists('TSA_Conversion_Table.pickle')):
        tsa_plate_id_to_file_mapper = pickle.load(open('TSA_Conversion_Table.pickle', 'rb'))
    
    stsa_df = pd.read_excel(args.path_to_PO_file, engine="openpyxl")
    stsa_df['Plate_ID'] = stsa_df['Plate_ID'].astype(str)
    if('Date of Measurement' not in stsa_df.columns):
        stsa_df['Date of Measurement'] = ""
    if('Time of Measurement' not in stsa_df.columns):
        stsa_df['Time of Measurement'] = ""
    
    src_tsa_layout = args.path_to_tsa_layout
    main_dir = args.main_dir_multiple
    for folder in os.listdir(main_dir):
        if(folder == '.DS_Store'):
            continue
        path = f'{main_dir}/{folder}'
        for raw_data_file in os.listdir(path):          
            split_s = raw_data_file.split('-')            
            if((raw_data_file.find('.csv') != -1) and (raw_data_file.find('Template_MD') != -1) and (not raw_data_file.startswith('.'))):           
                is_passed = True
                plate_id = 0
                if(raw_data_file.find('Template_MD') != -1):
                    print(raw_data_file)
                    raw_df = pd.read_csv(f'{path}/{raw_data_file}', sep=";", encoding="latin1")
                    plate_id = list(raw_df[raw_df['Cy5']=='Title:']['SampleID'])[0]
                else:
                    is_passed = False
                if(is_passed):
                    if(plate_id not in tsa_plate_id_to_file_mapper):
                        tsa_plate_id_to_file_mapper[plate_id] = raw_data_file
                    
                    the_path = f'{args.output_path}/{folder}'
                    if(args.extract_type == 'root_dir'):
                        the_path = args.output_path
                        
                    csv_file = f'{path}/{raw_data_file}'
                    with open(csv_file, "r", encoding="ISO-8859-1") as f:
                        first_line = f.readline()
                        delimiter = csv.Sniffer().sniff(first_line).delimiter

                    if(raw_data_file.find('Template_MD') != -1):
                        delimiter = ';'                    
                    tsa_raw_df = pd.read_csv(csv_file, encoding="ISO-8859-1", usecols=[0, 1], header=None, sep=delimiter)

                    date_time = tsa_raw_df[tsa_raw_df[0]=='Date/Time:'][1].to_numpy()[0]
                    split_date_time = date_time.split()
                    date_value = split_date_time[0]
                    time_value = split_date_time[1]
                    time_value = pd.to_datetime(time_value, format='%H:%M:%S').time()
                    date_value = pd.to_datetime(date_value, format='%d/%m/%Y').date()
                    stsa_df.loc[stsa_df['Plate_ID'] == plate_id, 'Date of Measurement'] = date_value
                    stsa_df.loc[stsa_df['Plate_ID'] == plate_id, 'Time of Measurement'] = time_value
                    plate_id = plate_id.strip()
                    os.makedirs(os.path.join(the_path, plate_id), exist_ok=True)
                    # os.makedirs(f'{the_path}/{plate_id}', exist_ok=True)
                    shutil.copy(f'{path}/{raw_data_file}', f'{the_path}/{plate_id}/TSA_RawData.csv')
                    shutil.copy(src_tsa_layout, f'{the_path}/{plate_id}/TSA_Layout.xlsx')
    stsa_df['Date of Measurement'] = stsa_df['Date of Measurement'].astype(str)
    stsa_df['Time of Measurement'] = stsa_df['Time of Measurement'].astype(str)
    stsa_df['Plate_ID'] = stsa_df['Plate_ID'].astype(str)
    stsa_df.to_excel(args.path_to_PO_file, index=False)
    pickle.dump(tsa_plate_id_to_file_mapper, open('TSA_Conversion_Table.pickle', 'wb'))
