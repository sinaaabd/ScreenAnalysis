#!/bin/bash

data=$1

echo "Here the data preparation starts ..."
echo "The data directory: $data"

# 1. Make folders at data
mkdir -p $data/raw_data
mkdir -p $data/analysis_data
mkdir -p $data/analysis_data/TSA_analysis
mkdir -p $data/analysis_data/SpSh_analysis

python download_data_to_nextcloud.py --username nlaubach --password tZywS-2eA9e-BTcDM-CgTp8-b5RK6 --assay_type SpectralShift --download_folder $data/raw_data --path_to_log_file my_log_file.log

python download_data_to_nextcloud.py --username nlaubach --password tZywS-2eA9e-BTcDM-CgTp8-b5RK6 --assay_type ThermalShiftAssay --download_folder $data/raw_data --path_to_log_file my_log_file.log

mv $data/raw_data/SpectralShift $data/raw_data/SpSh
mv $data/raw_data/ThermalShiftAssay $data/raw_data/TSA

echo "Data downloaded!"
exit 0
