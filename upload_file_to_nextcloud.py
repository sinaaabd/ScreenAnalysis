import requests
import pandas as pd
from io import StringIO
from xml.etree import ElementTree
import os
import argparse



if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', required=True, help='The Nextcloud username.')
    parser.add_argument('--password', required=True, help='The Nextcloud "app" password.')
    parser.add_argument('--upload_path', required=True, help='The path you intend to upload on Nextcloud! For instance, "Analysis"')
    parser.add_argument('--path_to_file', required=True, help='The path of the file (result).')

    args = parser.parse_args()
    USERNAME = args.username
    PASSWORD = args.password
    upload_path = args.upload_path
    path_to_file = args.path_to_file

    BASE_URL = f'https://nextcloud.iniuva.exanio.cloud/remote.php/dav/files/{USERNAME}/AI-DD%20platform/340K_Screen'
    filename = path_to_file.split('/')[-1]
    upload_url = f'{BASE_URL}/{upload_path}/{filename}'

    with open(path_to_file, 'rb') as f:
        response = requests.put(upload_url, data=f, auth=(USERNAME, PASSWORD))

    if response.status_code in [200, 201, 204]:
        print(f"Successfully uploaded '{filename}' to '{upload_url}'")
    else:
        print(f"Upload failed: HTTP {response.status_code} - {response.text}")
