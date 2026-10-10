import argparse
import pandas as pd

if(__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_to_PO_file', required=True, help='The PO xlsx file path.')
    parser.add_argument('--path_to_pp', required=True, help='The xlsx file containing mapping of Plate_ID and Protein.')
    args = parser.parse_args()

    PO_df = pd.read_excel(args.path_to_PO_file, engine="openpyxl")
    PO_df['Plate_ID'] = PO_df['Plate_ID'].astype("string")
    if('Protein' in PO_df.columns):
        PO_df = PO_df.drop(columns=['Protein'])
    pp_df = pd.read_excel(args.path_to_pp, engine="openpyxl")

    pp_df['Plate_ID'] = pp_df['Plate_ID'].astype("string")
    pp_df['Protein'] = pp_df['Protein'].astype("string")
    
    ddf = pd.merge(PO_df, pp_df, on='Plate_ID', how='inner', suffixes=('_old_PO', ''))[['Cxsmiles', 'Spectral_Shift', 'Thermal_Shift', 'Plate_ID', 'Protein']]

    PO_df = pd.merge(PO_df, pp_df, on='Plate_ID', how='inner')
    PO_df.to_excel(args.path_to_PO_file, index=False)    
