#!/bin/bash

data=$1

echo "Here the data analysis starts ..."
echo "The data directory: $data"

# 1. DMSO analysis, calculating deltaTm and deltaSpSa
python delta_value_calculation.py --PO_table_path $data/analysis_data/PO-ini2810.xlsx

echo "Script executed successfully :)"
exit 0
