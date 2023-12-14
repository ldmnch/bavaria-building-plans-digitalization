import requests
from requests.exceptions import HTTPError
import pandas as pd
import json

def parse_json(url = 'https://geoportal.bayern.de/bauleitplanungsportal/data/gemeinden.json'):

    '''
    Reads JSON file in an url and saves it as an object.

    Args:
        url : url to be parsed.

    Returns:
        jsonResponse : String that contains the JSON. 

    '''

    try:
        response = requests.get(url)
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    return(jsonResponse)

def format_json_data(json_results):

    '''
    Takes as input JSON in string and transforms it into a dictionary.

    Args:

        json_results : JSON file in a string.

    Returns:

        json_data : dictionary. 
    
    '''

    response_to_dictionary = {item['name']:item for item in json_results}

    json_data = json.dumps(response_to_dictionary)

    return(json_data)

def write_results(json_data,
                  output_folder,
                  file_name):
    
    '''
    Takes as input dictionary and outputs it to a folder.

    Args: 
        json_data: dictionary. 
        output_folder: string with name of folder. 
        file_name: string with name of file. 
    
    '''
    
    file_name = f'data/{output_folder}/{file_name}.json'

    # Write JSON string to a file
    with open(file_name, 'w') as file:
        file.write(json_data)    