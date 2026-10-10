import argparse
import pandas as pd

if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_PO_file', required=True, help='The PO xlsx file path.')
    parser.add_argument('--path_to_DMSO_TSA_file', required=False, help='The path to the DMSO controls CSV file for TSA.')
    parser.add_argument('--path_to_DMSO_SpSh_file', required=False, help='The path to the DMSO controls CSV file for SpSh.')
    args = parser.parse_args()
    
    if(not(args.path_to_DMSO_TSA_file or args.path_to_DMSO_SpSh_file)):
        print("Please use at least one of the following options: --path_to_DMSO_TSA_file, --path_to_DMSO_SpSh_file")
        exit(0)
    
    stsa_df = pd.read_excel(args.path_to_PO_file, engine="openpyxl")
    
    if(args.path_to_DMSO_TSA_file):
        print("Computing Delta-Tm: ")
        tsa_dmso_df = pd.read_csv(args.path_to_DMSO_TSA_file)
        tsa_dmso_df = tsa_dmso_df[['Plate_ID','Mean', 'STD']]
        stsa_df = stsa_df.merge(tsa_dmso_df, on='Plate_ID', how='left')
        stsa_df['deltaTm'] = stsa_df['Mean'] - stsa_df['Thermal_Shift']
        stsa_df = stsa_df.drop(columns=['Mean'])
        stsa_df = stsa_df.rename(columns={'STD':'Tm-STD'})
        
    if(args.path_to_DMSO_SpSh_file):
        print("Computing Delta-SpSh: ")
        SpSh_dmso_df = pd.read_csv(args.path_to_DMSO_SpSh_file)
        SpSh_dmso_df = SpSh_dmso_df[['Plate_ID','Mean', 'STD']]
        stsa_df = stsa_df.merge(SpSh_dmso_df, on='Plate_ID', how='left')
        stsa_df['deltaSpSh'] = stsa_df['Mean'] - stsa_df['Spectral_Shift']
        stsa_df = stsa_df.drop(columns=['Mean'])
        stsa_df = stsa_df.rename(columns={'STD':'SpSh-STD'})
    print("Saving Information into the PO Excel file...")    
    stsa_df.to_excel(args.path_to_PO_file, index=False)
