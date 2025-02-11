import os
import pandas as pd
import random
import easyocr
import tqdm 

from loguru import logger

def pdf_parser_from_path(pdf_path: str,
                         reader: easyocr.Reader) -> dict:
    """Parse pdf and extract content and metadata

    Args:
        pdf_path: path as string

    Returns:
        parsed: dictionary containing content and metadata
    """
    # try parsing with extended timeout, extract and store relevant inf

    try:
        result = reader.readtext(pdf_path, detail = 0)
        return {
            "content": result
        }
    
    # store error message if unsuccessful
    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return {
            "content": f"Error parsing PDF: {e}",
            "metadata": None
        }


def pdf_parser_from_folder(folder_path: str,
                           reader: easyocr.Reader,
                           sample_size: int = None) -> pd.DataFrame:
    """Apply pdf_parser_from_path function to full folder

    Args:
        folder_path: full input folder path as string

    Returns:
        df: df containing filename, content and metadata per pdf
    """
    # get all filenames
    pdf_files = [file for file in os.listdir(folder_path)
                 if file.lower().endswith('.pdf') or file.lower().endswith('.jpg')]
    
    # if a sample_size is specified, get random sample of specified size
    if sample_size is not None:
        # only if enough samples are available
        if sample_size <= len(pdf_files):
            pdf_files = random.sample(pdf_files, sample_size)
        # otherwise raise value error
        else:
            raise ValueError(f"Sample of {sample_size} larger than folder contents of {len(pdf_files)}")

    # define empty df to store parsed result
    parsed_data = []

    # iterate over all files in folder
    for pdf_file in tqdm(pdf_files, total=len(pdf_files)):
        #logger.info(f"Parsing file: {pdf_file}")
        pdf_path = os.path.join(folder_path, pdf_file)

        # apply parser function
        parsed_info = pdf_parser_from_path(pdf_path, reader)
        parsed_data.append({
            "filename": pdf_file,
            "content": parsed_info["content"]})

    logger.info("Parsing done.")
    # save as df and convert 'content' to string
    df = pd.DataFrame(parsed_data)

    return df