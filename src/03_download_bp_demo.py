# %%
#import pandas as pd
#import numpy as np
#import json
import geopandas as gpd
from pdfs_to_text import pdfs_downloader, pdfs_preprocessing

# %% [markdown]
# # Downloading PDFs
# 
# In the first notebooks, we obtained the information about building plans and the links to the respective PDFs. In this notebook, you will see how to use the function that takes as input that metadata and downloads all PDFs.
# 
# First, read the metadata:

# %%
filename = './data/proc/building_plans/building_plans_metadata.geojson'

# %%
data = gpd.read_file(filename)

# %% [markdown]
# - Adjust `id_column` with the name of the ID column.
# - Adjust `link_column` with the name of the column that contains the links.
# - Adjust `date_column` to the column with date of the building plans.
# - Adjust `output_folder` with name of the folder you want to save the data to.
# 
# The function also contains the optional parameter `sample_n` which can be used to only download a sample, defining the number of observations to take.

# %%
pdfs_downloader.run_pdf_downloader(input_df = data,
    id_column = 'id',
    link_column = 'URL zur Legende',
    output_folder = "./data/raw/building_plan_sample/pdfs",
    sample = False)

# %% [markdown]
# Then, we run the function run_pdfs_split that converts pdfs into jpg for the OCR.

# %%
pdfs_preprocessing.run_pdfs_split(input_folder='./data/raw/building_plan_sample/pdfs',
                                  output_folder= './data/proc/building_plans_sample/split_pdf/')


