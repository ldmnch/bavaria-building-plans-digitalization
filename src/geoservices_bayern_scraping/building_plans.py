import pandas as pd 
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import time
from tqdm import tqdm 
import random

def parse_url(url):

    '''
    Reads a url and parses its content as BeautifulSoup object.

    Args

        url : string with url to read. 

    Returns:

        BeautifulSoup object parsed.

    '''
    
    response = requests.get(url)
    
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    return(soup)

def scrape_all_table_rows(soup):
    '''
    Reads BeautifulSoup object with parsed html and reads all lines of a table. 

    Args:
        soup : BeautifulSoup object

    Returns:

        list with rows of table. 

    '''

    table = soup.find('table')

    rows = []

    for tr in table.find_all('tr'):

        row = [td.text for td in tr.find_all('td')]
        
        rows.append(row)

    return(rows)

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

def scrape_geoservices_api(url):

    parsed_site = parse_url(url)

    rows_list = scrape_all_table_rows(parsed_site)

    scraped_rows = split_list_by_value(rows_list, 'Auskunft Bauleitplanung (Bebauungsplan)')

    data = convert_list_of_results_to_dataframe(scraped_rows)

    return(data)

def scrape_bounding_boxes(boxes,
                          max_retries = 5, 
                          output_folder = 'geoservices_results'):
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

    max_retries = max_retries
    retry_count = 0

    for box in tqdm(boxes):
        
        try:
            
            url = 'https://geoservices.bayern.de/mapserver4bauleitbvv/bauleitplan_intern?VERSION=1.1.1&REQUEST=GetFeatureInfo&SRS=EPSG:31468&LAYERS=bplan_rechtskraft_lvg&STYLES=&BBOX='+box+'&WIDTH=4&HEIGHT=4&QUERY_LAYERS=bplan_rechtskraft_lvg&X=2&Y=2&FORMAT=image/png&INFO_FORMAT=text/html&FEATURE_COUNT=5000&EXCEPTIONS=application/vnd.ogc.se_xml'

            data = scrape_geoservices_api(url)
                
            data.to_csv(f'{output_folder}/bounding_box_{box}.csv', index=False)

            time.sleep(10)
                
        except AttributeError as ae:

            time.sleep(10)

            continue

        except HTTPError or requests.exceptions.ConnectTimeout:

            retry_count += 1 

            if retry_count < max_retries:

                time.sleep(30)

            else:

                continue

def scrape_in_batches(bounding_boxes, 
                      batch_size,
                      batch_delay,
                      max_retries,
                      output_folder):
    
    
    for i in range(0, len(bounding_boxes), batch_size):

        bounding_boxes_batch = bounding_boxes[i:i+batch_size]

        print('Running batch '+str(i)+' of '+str(len(bounding_boxes))+' bounding boxes.')

        scrape_bounding_boxes(bounding_boxes_batch,
                          max_retries = max_retries, 
                          output_folder = output_folder)
        
        time.sleep(batch_delay)
