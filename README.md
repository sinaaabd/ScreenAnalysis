# Iniuva's Screen Analysis

This repository contains code for analyzing Iniuva's screen.

In the follwoing, we explain the details needed to run the analysis.

## Conda environment

```
conda create -n screen python=3.11
conda activate screen

conda install -c conda-forge numpy pandas scikit-learn matplotlib seaborn requests tqdm
pip install openpyxl
```
**Note:** We may still have some missing packages in the code above. In case of any package error, plz contact Behnam.


## Organizing the data directory

Before we run the code, the data needs to be organized as in the follwoing:
```
data
├── raw_data
│   ├── SpSh: CSV files of SpSh are named after their plate IDs and stored in folders organized by date. will be created and filled by nextcloud_download.sh
│   └── TSA: CSV files of TSA stored in folders organized by date. will be created and filled by nextcloud_download.sh
└── analysis_data
    ├── SpSh_analysis: empty, will be created and filled by run_data_preparation.sh
    ├── TSA_analysis: empty, will be created and filled by run_data_preparation.sh
    ├── PO-ini2810.xlsx: the result table
    ├── Assignment-Plate_ID_Protein.xlsx
    └── TSA_Layout.xlsx: TSA layout file
```

**Note:** The current version of the code runs any file insde ```data/raw_data/```. In the future, we may add some modifications on this.

## Step 0. Download data
### Download data from ThermalShiftAssay and SpectralShift

To download from Nextcloud, firstly you need to insert your Nextcloud app username and password using arguments "--username" and "--password" arguments, respectively.
Then, you need to specify the directory of interest using "--assay_type" argument with two options of either ThermalShiftAssay or SpectralShift. Finally, you need to specify the directory (or path) on your personal computer (or laptop) to save the downloaded files using "--download_folder" argument. We have two pickle files: SpSh_Conversion_Table.pickle and TSA_Conversion_Table.pickle which are files that track which CSV files have already been downloaded from Nextcloud. This allows subsequent runs to skip re-downloading the same files, saving time and resources. When we use the tsa_preprocessing_add_date_time and ssa_preprocessing scripts, the plate ID and file names are recorded, enabling the scripts to avoid redundant downloads and re-analysis in future runs. Additionally, you must specify the log file containing the Plate_IDs that already analyzed and the values are inserted into the PO table. Please note that each line of the log file shows a Plate_ID. In case that there is no log file, please create an empty file as the log file and use it as the input of the --path_to_log_file argument.

```
python download_data_to_nextcloud.py --username YOUR_NEXTCLOUD_APP_USERNAME --password YOUR_NEXTCLOUD_APP_PASSWORD --assay_type ASSAY_TYPE --download_folder SAVE_DIR --path_to_log_file LOG_FILENAME
```

## Step 1. data preparation
### Run all data preparation at once

To run the whole analysis, we prepared the script ```run_screen.sh``` as

```
./run_data_preparation.sh path/to/data
```
Just wait for the result :)

Note: the path to the file should not contain any ```.``` (e.g. ```../``` will lead to error).

### Run each step separately
#### I. Thermal shift assay (TSA)

1. Run ```tsa_preprocessing_add_date_time.py``` to organize files for the TSA analysis at ```data/analysis_data/TSA_analysis```, copies from raw folder to analysis folder and fit to template, and adds time and date to the PO table. It also utilizes a Plate_ID to file name mapper "TSA_Conversion_Table.pickle" and this mapper is updated when we call this function. Note that, in case of using GCDH data, since we have a new naming format, you must use ```tsa_preprocessing_add_date_time_gcdh.py```.

```
python tsa_preprocessing.py --main_dir_multiple data/raw_data/TSA --path_to_tsa_layout data/analysis_data/TSA_Layout.xlsx --output_path data/analysis_data/TSA_analysis --extract_type root_dir
```

2. Run ```TSA_analysis_main.py``` to get the TSA results

```
python tsa_analysis_main.py --working_dir_bulk data/analysis_data/TSA_analysis
```

3. Add the result of TSA analysis to PO table

```
python tsa_info_to_main_excel.py --path_to_tsa data/analysis_data/TSA_analysis --path_to_main_excel data/analysis_data/PO-ini2810.xlsx
```

#### II. Spectral shift assay (SpSh)

1. Run ```ssa_preprocessing.py``` to organize files for the SpSh analysis at ```data/analysis_data/SpSh_analysis```, copies from raw folder to analysis folder and fit to template. It also utilizes a Plate_ID to file name mapper "SpSh_Conversion_Table.pickle" and this mapper is updated when we call this function.

```
python ssa_preprocessing.py --main_dir data/raw_data/SpSh --output_path data/analysis_data/SpSh_analysis
```

2. Run ```ssa_info_to_main_excel.py``` to get SSA results and add them to PO table.

```
python ssa_info_to_main_excel.py --path_to_ssa data/analysis_data/SpSh_analysis --path_to_main_excel data/analysis_data/PO-ini2810.xlsx 
```

If you are using a newer version of the files (for instance GCDH), you must use the following command (this includes the normalization of the data based on the DMSO values - (A02_upper - Mean_upper)/(A02_lower - Mean_lower)):

```
python ssa_info_to_main_excel_gcdh.py --path_to_ssa data/analysis_data/SpSh_analysis --path_to_main_excel data/analysis_data/PO-ini2810.xlsx 
```



#### Post processing

1. Run ```plate_id_protein_mapping.py``` to add protein names as a new column.

## Step 2. data analysis

### I. DMSO analysis, calculating deltaTm and deltaSpSa
Run ```delta_value_calculation.py``` to obtain deltaTm, deltaSpSa, as well as warnings and add them to the PO table.

## Step 3. Upload File(s) to Nextcloud
### Upload the PO table to Nextcloud

To upload the result PO table to Nextcloud, firstly you need to insert your Nextcloud app username and password using arguments "--username" and "--password" arguments, respectively.
Then, you need to specify the directory of interest on Nextcloud using "--upload_path" argument, for example "Analysis" directory.  
Finally, you need to specify the result file name (The final PO table) and its path in your personal computer (or laptop) using "--path_to_file" argument.


```
python upload_file_to_nextcloud.py --username YOUR_NEXTCLOUD_APP_USERNAME --password YOUR_NEXTCLOUD_APP_PASSWORD --upload_path DIR_IN_NEXTCLOUD --path_to_file FILE_NAME_AND_ITS_PATH
```

