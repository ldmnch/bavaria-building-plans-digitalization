import pandas as pd 
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import time
from tqdm import tqdm 
import random
import os

def parse_url(url : str = "https://geoportal.bayern.de/ba-backend/getFeature", 
              easting_northing : list = [4503718.338133049, 5407116.539337536]):

    '''
    Reads a url and parses its content as BeautifulSoup object.

    Args

        url : string with url to read. 

    Returns:

        BeautifulSoup object parsed.

    '''

    payload = {
    "id": "26d2b2b8-3944-4a49-aec2-59f827d9aa9e",
    "resolution": 4,
    "easting": easting_northing[0],
    "northing": easting_northing[1],
    "password": "",
    "srid": "31468",
    "username": ""
    }

    response = requests.post(url, json=payload)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    return(soup)

def scrape_all_tables(soup):
    '''
    Reads BeautifulSoup object with parsed html and reads all lines of a table. 

    Args:
        soup : BeautifulSoup object

    Returns:

        list with rows of table. 

    '''

    tables = soup.find_all('table')

    plans = []

    for table in tables:
    # Initialize a dictionary for each plan
        plan = {}
        
        # Extract the table rows
        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) == 2:
                key = columns[0].get_text(strip=True)
                value = columns[1].get_text(strip=True)
                # Extract hyperlink if present
                link = columns[1].find('a')
                if link and link['href']:
                    value = link['href']
                plan[key] = value
        
        # Add the plan to the list
        plans.append(plan)

    return(plans)

def split_list_by_value(lst, 
                        value = 'Auskunft Bauleitplanung (Bebauungsplan)'):
    
    '''
    Takes as input a list and splits into sub-lists using as separator the defined value. 

    Args:
        lst : list that will be separated
        value : value to use as separator 

    Returns: 
        sublists : list of lists with the values separated 
    '''
    sublists = []
    temp_list = []

    for item in lst:
        if item == [value]:
            if temp_list:
                sublists.append(temp_list)
                temp_list = []
        else:
            temp_list.append(item)

    if temp_list:
        sublists.append(temp_list)

    return sublists

def convert_results_to_dictionary(result):
    '''
    Takes as input a list of lists with two values. Takes each element of the list and appends it to a dictionary as a key-value pair. 

    Args:
        result : list which contains two values per element. 

    Returns: 
        result_dict : list converted to dictionary. 
    '''

    result_dict = {}

    for inner_list in result:

        key = inner_list[0]
        value = inner_list[1]

        result_dict[key] = value

    return(result_dict)

def convert_list_of_results_to_dataframe(list_of_rows):
    '''
    Takes as input a list with dictionaries, maps the function convert_results_to_dictionary() on each element. Creates dataframe from those dictionaries. 

    Args:
        list_of_rows : list of lists with two values which will be mapped as dict. 
    
    Returns: 
        result_data : dataframe. 
    '''

    result_dictionary = [convert_results_to_dictionary(item) for item in list_of_rows]

    result_data = pd.DataFrame(result_dictionary)

    return(result_data)

def scrape_geoservices_api(url : str, 
                           easting_northing : list = [4503718.338133049, 5407116.539337536]):

    parsed_site = parse_url(url)

    rows_list = scrape_all_tables(parsed_site)

    data = pd.DataFrame(rows_list)

    return(data)

def scrape_bounding_boxes(data_gemeinden, 
                          max_retries : int = 5, 
                          output_folder : str ='geoservices_results'):
    '''
    Scrapes tables of building plans in geoservices Bayern for different bounding boxes. Writes outputs as csv. 

    Args: 
        boxes : List of strings with bounding boxes. 
        max_retries : Maximum number of retries for each page.
        retry_delay: Delay time between retries in seconds. 
        output_folder: Name of folder to output results to. 

    Returns: 
        saved data files to output_folder. 
    ''' 

    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for index, row in tqdm(data_gemeinden.iterrows()):

        retry_count = 0
        
        while retry_count < max_retries:
            
            try:

                data = scrape_geoservices_api(url = 'https://geoportal.bayern.de/ba-backend/getFeature', easting_northing=row['midpoint'])
                name = row['name']
                data.to_csv(f'{output_folder}/building_plans_{name}.csv', index=False)
                time.sleep(10)
                break  # Exit the retry loop on success
            
            except AttributeError as ae:
                time.sleep(10)
                with open(f'{output_folder}/logs.txt', 'a') as log_file:
                    log_file.write(f"Box {name}: An error occurred - {str(ae)}\n")
                break  # Exit the retry loop on AttributeError
            
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError, requests.exceptions.SSLError) as he:
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(30)
                else:
                    with open(f'{output_folder}/logs.txt', 'a') as log_file:
                        log_file.write(f"Box {name}: An error occurred - {str(he)}\n")
                    break  # Exit the retry loop after max retries


def scrape_in_batches(data_gemeinden : pd.DataFrame, 
                      batch_size : int = 100,
                      batch_delay : int = 30,
                      max_retries : int = 5,
                      output_folder : str = 'geoservices_results',
                      size_n : int = 100):
    
    if size_n:
        data_gemeinden = data_gemeinden.sample(n = size_n)
    
    for i in range(0, len(data_gemeinden), batch_size):

        gemeinden_batch = data_gemeinden[i:i+batch_size]

        print('Running batch '+str(i)+' of '+str(len(data_gemeinden))+' bounding boxes.')

        scrape_bounding_boxes(gemeinden_batch,
                          max_retries = max_retries, 
                          output_folder = output_folder)
        
        time.sleep(batch_delay)
