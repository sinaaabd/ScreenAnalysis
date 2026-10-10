# Iniuva's Screen Analysis

For single experiment analysis, you need to specify a working directory, which should contain ```TSA_Layout.xlsx``` and ```TSA_RawData.xlsx```. Then run

```
python tsa_analysis_main.py --working_dir path/to/the/folder
```

For multiple experiment analysis (bulk), you need to specify a root directory which contains several folders each with corresponding ```TSA_Layout.xlsx``` and ```TSA_RawData.xlsx```.

```
python tsa_analysis_main.py --working_dir_bulk path/to/the/folder
```

In both cases, all the results will further be compressed as a *zip* file.

TSA preprocessing: To create folders with the name same as csv files (raw data - Plate ID) if we have multiple experiments
```
python tsa_preprocessing.py --main_dir_multiple path/to/the/folder
```

TSA preprocessing: To create folders with the name same as csv files (raw data - Plate ID) if we have single experiment
```
python tsa_preprocessing.py --main_dir_single path/to/the/folder
```
You can also use --extract_type option to declare whether you want to extract in the root directory or in the sub-directories. There are two option: 'separate_dirs' or 'root_dir' (default: root_dir)

You also need to insert the path of the output folder using --output_path argument.

SpSh preprocessing: To create folders with the name same as csv files (raw data - Plate ID) when we have multiple experiments
```
python ssa_preprocessing.py --main_dir path/to/the/SpSh_folder --output_path path/to/the/output/dir
```

To add the Thermal Shift Assay data into the main Excel File, which contains all information about the experiments:
```
python tsa_info_to_main_excel.py --path_to_tsa path/to/the/TSA/folder --path_to_main_excel path/to/the/main/Excel/file --output_file path/to/the/output/file.xlsx
```
Note: --output_file is an optional argument, if you do not declare it then by default the program replaces the main Excel file.

Note: You can also modify options: --well_col, --tm_col, and --tsa_filename if necessary. By default, they have 'compound', 'tm2_1', and 'result.csv', respectively.

To add the Spectral Shift Assay data into the main Excel File, which contains all information about the experiments:
```
python ssa_info_to_main_excel.py --path_to_ssa path/to/the/SSA/folder --path_to_main_excel path/to/the/main/Excel/file --output_file path/to/the/output/file.xlsx
```
Note: --output_file is an optional argument, if you do not declare it then by default the program replaces the main Excel file.



=========




1. run tsa_preprocessing (test OK)

```
python tsa_preprocessing.py --main_dir_multiple data/raw_data/TSA --path_to_tsa_layout data/analysis_data/TSA_Layout.xlsx --output_path data/analysis_data/TSA_analysis --extract_type root_dir
```

2. Run TSA_analysis_screen (test OK)

```
python tsa_analysis_main.py --working_dir_bulk data/analysis_data/TSA_analysis
```

3. Add the result of TSA analysis to PO table (test OK)

```
python tsa_info_to_main_excel.py --path_to_tsa data/analysis_data/TSA_analysis --path_to_main_excel data/analysis_data/PO-ini2810.xlsx
```

4. run ssa_preprocessing (test OK)

```
python ssa_preprocessing.py --main_dir data/raw_data/SpSh --output_path data/analysis_data/SpSh_analysis
```

5. SSA process (will be updated by Sina)

```
python ssa_info_to_main_excel.py --path_to_ssa data/analysis_data/SpSh_analysis --path_to_main_excel data/analysis_data/PO-ini2810.xlsx 
```
====