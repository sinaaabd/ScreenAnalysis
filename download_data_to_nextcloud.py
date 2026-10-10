import requests
import pandas as pd
from io import StringIO
from xml.etree import ElementTree
import os
import argparse
import pickle


def list_folder_contents(base_url, username, password, folder_name):
    target_url = f'{base_url}/{folder_name}'
    headers = {
        "Depth": "1", 
        "Content-Type": "application/xml"
    }

    data = '''<?xml version="1.0"?>
    <d:propfind xmlns:d="DAV:">
      <d:prop>
        <d:resourcetype/>
        <d:displayname/>
      </d:prop>
    </d:propfind>'''

    try:
        response = requests.request("PROPFIND", target_url, data=data, headers=headers, auth=(username, password))
        if(response.status_code != 207):
            print(f"Failed to fetch contents: {response.status_code}")
            return {'folders': [], 'files': []}

        xml_tree = ElementTree.fromstring(response.content)
        ns = {'d': 'DAV:'}
        folders, files = [], []

        for elem in xml_tree.findall('d:response', ns):
            href = elem.find('d:href', ns).text
            resourcetype = elem.find('.//d:resourcetype', ns)

            # Skip the folder itself
            if(href.rstrip('/') == target_url.rstrip('/')):
                continue

            item_name = href.rstrip('/').split('/')[-1]

            if(resourcetype is not None and resourcetype.find('d:collection', ns) is not None):
                if(item_name != folder_name):
                    folders.append(item_name)
            else:
                files.append(item_name)

        return {'folders': folders, 'files': files}

    except Exception as e:
        print(f"Error: {e}")
        return {'folders': [], 'files': []}


if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', required=True, help='The Nextcloud username.')
    parser.add_argument('--password', required=True, help='The Nextcloud "app" password.')
    parser.add_argument('--assay_type', choices=['ThermalShiftAssay', 'SpectralShift'], default='ThermalShiftAssay')
    parser.add_argument('--download_folder', required=True, help='The path where you want to save the data.')
    parser.add_argument('--path_to_log_file', required=True, help='Specify the path and the name of the log file.')

    args = parser.parse_args()
    download_folder = args.download_folder
    assay_type = args.assay_type
    USERNAME = args.username
    PASSWORD = args.password
    
    done_files = []
    if(os.path.exists('SpSh_Conversion_Table.pickle') and os.path.exists('TSA_Conversion_Table.pickle')):
        conversion_table = {}
        if(assay_type == 'ThermalShiftAssay'):
            conversion_table = pickle.load(open('TSA_Conversion_Table.pickle', 'rb'))
        else:
            conversion_table = pickle.load(open('SpSh_Conversion_Table.pickle', 'rb'))

        if(not os.path.exists(args.path_to_log_file)):
            open(args.path_to_log_file, 'w').close()
            
        with open(args.path_to_log_file, 'r') as file:
            for plate_id in file:
                plate_id = plate_id.strip()
                filename = conversion_table[plate_id]
                if(filename not in done_files):
                    done_files.append(filename)
    else:
        print("WARNING: The SpSh_Conversion_Table.pickle and TSA_Conversion_Table.pickle files do not exist!")
        print("We are going to download all files then!")
    
    BASE_URL = f'https://nextcloud.iniuva.exanio.cloud/remote.php/dav/files/{USERNAME}/AI-DD%20platform/340K_Screen/RawData%20and%20Log%20Files'
    TARGET_URL = f"{BASE_URL}/{assay_type}"
    
    folder_path = f"{download_folder}/{assay_type}"
    if(not os.path.exists(folder_path)):
        os.makedirs(folder_path)

    contents = list_folder_contents(BASE_URL, USERNAME, PASSWORD, assay_type)
    for subfolder in contents['folders']:
        folder_path = f"{download_folder}/{assay_type}/{subfolder}"
        if(not os.path.exists(folder_path)):
            os.makedirs(folder_path)
        subfolder_url = f'{BASE_URL}/{assay_type}'
        subfolder_contents = list_folder_contents(subfolder_url, USERNAME, PASSWORD, subfolder)
        for csv_file in subfolder_contents['files']:
            if((csv_file.find(".csv") != -1) and (csv_file not in done_files)):
                csvfile_url = f'{subfolder_url}/{subfolder}/{csv_file}'
                print(f'Downloading file: {subfolder}/{csv_file}')
                response = requests.get(csvfile_url, auth=(USERNAME, PASSWORD))

                local_path = f'{folder_path}/{csv_file}'
                if(response.status_code == 200):
                    with open(local_path, 'wb') as f:
                        f.write(response.content)
                else:
                    print(f"Failed to download {csv_file} - HTTP {response.status_code}")
