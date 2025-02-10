# %%
from pdfs_to_text import pdfs_parser

import easyocr

# %% [markdown]
# # Parsing PDF content
# 
# Once we have the PDFs downloaded it is necessary to parse the content into text so we can analyze it. First:
# 
# - Assign to `BP_PDF_DIR` the directory where you have all the PDFs downloaded.
# - Change `BP_TEXT_FILE_PATH_JSON` to the path and file name you want the output to be saved as.

# %%
BP_PDF_DIR = './data/proc/building_plans_sample/split_pdf/'
BP_TEXT_FILE_PATH_JSON = './data/proc/building_plans_sample/bp_text.json'

# %%
reader = easyocr.Reader(['de'], gpu=False)

# %%
parsed_pdfs_df = pdfs_parser.pdf_parser_from_folder(folder_path=BP_PDF_DIR, reader = reader)

# %%
parsed_pdfs_json = parsed_pdfs_df.to_json(orient='records')

# %%
with open(BP_TEXT_FILE_PATH_JSON, 'w') as outputfile:
    outputfile.write(parsed_pdfs_json)

# %% [markdown]
# As a result, this reads all PDFs in the specified folder, parses them with OCR and outputs the results of the content to a JSON in the defined path. 


