import os
from datetime import datetime
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

def parse_date(date_string):
    try:
        return pd.to_datetime(date_string)
    except ValueError:
        return np.nan


def is_downloadable(url):
    """
    Does the url contain a downloadable resource?
    """
    h = requests.head(url, allow_redirects=True, timeout=3)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower() or 'html' in content_type.lower():
        return False
    return True


def filtering_useful_data(date_column: str,
                          start_date: str,
                          end_date: str,
                          data: pd.DataFrame):
    """
    Takes as input Geodataframe, parses the dates, filters BP from 2012 and onwards and keeps only PDF files. 
    """

    # Parse date column into date format
    data[date_column] = data[date_column].apply(parse_date)

    # Define the start date for filtering
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter rows which the date is 2012 and onwards
    filtered_data = data[(data[date_column] >= start_date) & (data[date_column] < end_date)]

    return filtered_data


def download_pdfs(link: str,
                  object_id: str,
                  output_folder: str,
                  timeout_seconds: int = 120):
    """ This function takes as input a link and downloads the PDFs to the output folder.

    It also returns the links and ids that failed to download.

    Args:
        link (str): Link to the PDF
        object_id (str): ID of the BP
        output_folder (str): Path to the folder where the PDFs will be saved

    Returns:
        error_links (list): List of links that failed to download
        error_ids (list): List of ids that failed to download
    """
    error_links = []
    error_ids = []
    try:
        # Check if the link contains downloadable content
        if is_downloadable(link):
            # Connect to link
            response = requests.get(link, timeout=timeout_seconds)

            if response.status_code == 200:
                # Define the pdf path
                pdf_name = object_id + (".pdf")
                pdf_path = os.path.join(output_folder, pdf_name)

                # Save the PDF content to a file
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(response.content)
                # print(f"Downloaded: {pdf_name}")
        else:
            # print(f"Failed to download: {link}")

            # If we get an error, append id and link to lists
            error_links.append(link)
            error_ids.append(object_id)

    except:
        # If we get an error, append id and link to lists
        error_links.append(link)
        error_ids.append(object_id)

    return error_links, error_ids


def run_pdf_downloader(input_df: pd.DataFrame,
                       id_column: str,
                       link_column: str,
                       date_column: str,
                       start_date: str,
                       end_date: str,
                       output_folder : str,
                       sample_n: int = None
                       ):
    """
    This function takes as input a dataframe with the links to the PDFs and downloads them to the output folder.


    Args:
        input_df (pd.DataFrame): DataFrame that contains the links to the PDFs.
        id_column (str): Name of ID column
        link_column (str): Column that contains the links
        date_column (str): Column that contains the dates
        output_folder (str): Path to the folder where the PDFs will be saved
        sample_n (int): Number of rows to sample from the input_df. If None, all rows are used.

    """

    # Make empty lists that append links that didn't scrape
    error_links = []
    error_ids = []

    input_df = filtering_useful_data(data = input_df, date_column = date_column, start_date=start_date, end_date=end_date)

    if sample_n:
        input_df = input_df.sample(n=sample_n, random_state=912)

    # Check if the output folder exists, if not creates it
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Iterate over rows of the dataframe
    # Loop through the DataFrame rows
    for index, row in tqdm(input_df.iterrows(), total=len(input_df)):
        link = row[link_column]
        object_id = str(row[id_column])  # Assuming 'id_column' holds the ID of the BP
        # Download PDFs and collect errors
        error_links_single, error_ids_single = download_pdfs(link=link,
                                                            object_id=object_id,
                                                            output_folder=output_folder)
        # Extend the error lists
        error_links.extend(error_links_single)
        error_ids.extend(error_ids_single)

    errors_df = pd.DataFrame.from_dict({'objectid': error_ids,
                                        'scanurl': error_links})

    errors_df.to_csv(output_folder + "/error_links.csv", index=False)