"""
    Thermal shift assay analysis for screening: main for gcdh
    Version 0.2.2
    Authors:
        - Nora Constanze Laubach (laubach@iniuva.com)
        - Behnam Yousefi (behnm.yousefi@zmnh.uni-hamburg.de; yousefi.bme@gmail.com)
    UKE, Hamburg, Germany - Jan 2025
"""

import os
import json
import argparse
from tqdm import tqdm
import shutil


if __name__ == "__main__":
    
    # Read inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--working_dir', required=False, help='Working directory for a single experiment.')
    parser.add_argument('--working_dir_bulk', required=False, help='Working directory for a multiple experiments.')
    parser.add_argument('--version', required=False, default='screen', help='code version: vanilla, screen')
    parser.add_argument('--zzzip', action='store_true', help='enable zzzzziping')

    args = parser.parse_args()
    working_dir = args.working_dir
    working_dir_bulk = args.working_dir_bulk
    version = args.version

    # Check for working directoty
    if working_dir == None and working_dir_bulk == None:
        stop('Either "working_dir" or "working_dir_bulk" should be defined')
    
    flag_bulk = working_dir_bulk != None
    if flag_bulk:
        working_dir = os.listdir(working_dir_bulk)
    else:
        working_dir = [working_dir]
    print(f'Number of experiments = {len(working_dir)}')
    
    # Loop over all experiments
    for wd in tqdm(working_dir):
        print(f'* Analysing {wd} ...')
        if flag_bulk:
            wd = os.path.join(working_dir_bulk, wd)
            ## Check if wd is not a folder or it is hidden, then pass
            if not (os.path.isdir(wd) or wd.find('.') >= 0):
                print(f'   Invalid file {wd}')
                continue
        ## Run tsa_analysis_screen_single
        try:
            if version == 'screen':
                os.system(f'python tsa_analysis_screen_single_gcdh.py --working_dir {wd}')
            else:
                stop(f'   Invalid version = {version}')
        except:
            print(f'   An error occurred when analysing {wd}')

    folder_to_zip = working_dir_bulk if flag_bulk else working_dir[0]
    zip_dir = folder_to_zip + '_results'

    print(f'* Done! Results save in {folder_to_zip}.')

    if args.zzzip:
        shutil.make_archive(zip_dir, 'zip', folder_to_zip)
        print(f'* Done! {zip_dir} zip file is created.')
