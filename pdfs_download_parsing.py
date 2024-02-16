import pandas as pd
import easyocr
from src.pdfs_to_text import pdfs_downloader, pdfs_preprocessing
from src.pdfs_to_text import pdfs_parser

data = pd.read_csv('data/proc/building_plans/building_plans_metadata.csv')

pdfs_downloader.run_pdf_downloader(input_df = data,
    id_column = 'id',
    link_column = 'URL zur Legende',
    date_column = 'Datum des Inkrafttretens',
    start_date = '2000-01-01',
    end_date = '2011-12-31',
    output_folder = "data/raw/building_plans/pdfs")

pdfs_preprocessing.run_pdfs_split(input_folder='data/raw/building_plans/pdfs',
                                  output_folder= 'data/proc/building_plans/split_pdf/')

