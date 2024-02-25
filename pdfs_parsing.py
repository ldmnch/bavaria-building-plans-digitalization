import pandas as pd
import easyocr

from src.pdfs_to_text import pdfs_parser

reader = easyocr.Reader(['de'], gpu=False)

RAW_PDFS_FOLDER_PATH = "data/raw/building_plans/pdfs"
SPLIT_PDFS_FOLDER_PATH = 'data/proc/building_plans/split_pdf/'
BP_TEXT_FILE_PATH_JSON = 'data/proc/building_plans/bp_text.json'

parsed_pdfs_df = pdfs_parser.pdf_parser_from_folder(folder_path=SPLIT_PDFS_FOLDER_PATH, reader = reader)

parsed_pdfs_json = parsed_pdfs_df.to_json(orient='records')

with open(BP_TEXT_FILE_PATH_JSON, 'w') as outputfile:
    outputfile.write(parsed_pdfs_json)
