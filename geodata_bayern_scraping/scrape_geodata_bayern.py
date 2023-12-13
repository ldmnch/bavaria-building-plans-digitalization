import requests
from requests.exceptions import HTTPError
import pandas as pd
import json

def parse_bauleitplanungsportal_json(url = 'https://geoportal.bayern.de/bauleitplanungsportal/data/gemeinden.json'):

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

    response_to_dictionary = {item['name']:item for item in json_results}

    json_data = json.dumps(response_to_dictionary)

    return(json_data)

def write_results(json_data,
                  output_folder,
                  file_name):
    
    file_name = f'data/{output_folder}/{file_name}.json'

    # Write JSON string to a file
    with open(file_name, 'w') as file:
        file.write(json_data)    