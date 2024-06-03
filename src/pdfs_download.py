import pandas as pd

from src.pdfs_to_text import pdfs_downloader, pdfs_preprocessing

data = pd.read_csv('data/proc/building_plans/building_plans_metadata.csv')
#reader = easyocr.Reader(['de'])

RAW_PDFS_FOLDER_PATH = "data/raw/building_plans/pdfs"
SPLIT_PDFS_FOLDER_PATH = 'data/proc/building_plans/split_pdf/'
BP_TEXT_FILE_PATH_JSON = 'data/proc/building_plans/bp_text.json'

#pdfs_downloader.run_pdf_downloader(input_df = data,
#    id_column = 'id',
#    link_column = 'URL zur Legende',
#    date_column = 'Datum des Inkrafttretens',
#    start_date = '2000-01-01',
#    end_date = '2011-12-31',
#    output_folder = RAW_PDFS_FOLDER_PATH)

pdfs_preprocessing.run_pdfs_split(input_folder=RAW_PDFS_FOLDER_PATH,
                                  output_folder= SPLIT_PDFS_FOLDER_PATH)


#parsed_pdfs_df = pdfs_parser.pdf_parser_from_folder(folder_path=SPLIT_PDFS_FOLDER_PATH, reader = reader)

#parsed_pdfs_json = parsed_pdfs_df.to_json(orient='records')

#with open(BP_TEXT_FILE_PATH_JSON, 'w') as outputfile:
#    outputfile.write(parsed_pdfs_json)