import geopandas as gpd
from pdfs_to_text import pdfs_downloader, pdfs_preprocessing, azure_blob_storage

filename = './data/proc/building_plans/building_plans_metadata.geojson'

# %%
data = gpd.read_file(filename)
data = data.sample(100)

blob_service_client = azure_blob_storage.azure_container_setup()
container_client = azure_blob_storage.create_azure_container

# %% [markdown]
# - Adjust `id_column` with the name of the ID column.
# - Adjust `link_column` with the name of the column that contains the links.
# - Adjust `date_column` to the column with date of the building plans.
# - Adjust `output_folder` with name of the folder you want to save the data to.

PdfDownloader = pdfs_downloader.PdfDownloader

# Instantiate with Azure upload function
downloader = PdfDownloader(
    input_df = data, 
    id_column = 'id', link_column = 'URL zur Legende',
    output_folder = "./data/raw/building_plan_sample/pdfs_subset",
    sample = False, 
    batch_size=10, 
    blob_service_client = blob_service_client, 
    azure_container = container_client, 
    azure_upload_blob = azure_blob_storage.azure_upload_blob
)

# Run the batch downloader
downloader.run_batch_pdf_downloader()


# %% [markdown]
# Then, we run the function run_pdfs_split that converts pdfs into jpg for the OCR.

# %%
#pdfs_preprocessing.run_pdfs_split(input_folder='./data/raw/building_plan_sample/pdfs',
#                                  output_folder= './data/proc/building_plans_sample/split_pdf/')


