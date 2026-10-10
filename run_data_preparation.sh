#!/bin/bash

data=$1

echo "Here the data preparation starts ..."
echo "The data directory: $data"

# 1. Make folders at data/analysis_data
mkdir -p $data/analysis_data/TSA_analysis
mkdir -p $data/analysis_data/SpSh_analysis

# 2. Organize files for the TSA analysis - copy from raw folder to analysis folder and fit to template
python tsa_preprocessing_add_date_time.py --main_dir_multiple $data/raw_data/TSA --path_to_tsa_layout $data/analysis_data/TSA_Layout.xlsx --output_path $data/analysis_data/TSA_analysis --path_to_PO_file $data/analysis_data/PO-ini2810.xlsx

# 3. Get the TSA results
python tsa_analysis_main.py --working_dir_bulk $data/analysis_data/TSA_analysis

# 4. Add the result of TSA analysis to PO table
python tsa_info_to_main_excel.py --path_to_tsa $data/analysis_data/TSA_analysis --path_to_main_excel $data/analysis_data/PO-ini2810.xlsx

# 5. Organize files for the SSA analysis - copy from raw folder to analysis folder and fit to template
python ssa_preprocessing.py --main_dir $data/raw_data/SpSh --output_path $data/analysis_data/SpSh_analysis

# 6. Get SSA results and add them to PO table
python ssa_info_to_main_excel.py --path_to_ssa $data/analysis_data/SpSh_analysis --path_to_main_excel $data/analysis_data/PO-ini2810.xlsx

# 7. Map protein names
python plate_id_protein_mapping.py --path_to_PO_file $data/analysis_data/PO-ini2810.xlsx --path_to_pp $data/analysis_data/Assignment-Plate_ID_Protein.xlsx


echo "Script executed successfully :)"
exit 0
