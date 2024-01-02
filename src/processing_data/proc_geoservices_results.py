import pandas as pd
import glob
import os 

def generate_dataset_building_plans(input_folder_path,
                                    output_folder_path,
                                    output_folder_name):

    all_files = glob.glob(f"{input_folder_path}/*.csv")

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    data = pd.concat(li, axis=0, ignore_index=True)

    data = data.drop_duplicates(subset=data.columns.difference(['id']))

    data.to_csv(f'{output_folder_path}/{output_folder_name}.csv', index_label = 'id')