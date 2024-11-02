import pandas as pd
import os
import re

from geoservices_bayern_scraping import building_plans

CWD = os.getcwd()

data_dir = os.path.join(CWD, 'data', 'raw', 'geoservices_results')
file_path = os.path.join(data_dir, 'logs.txt')

# Check if the file exists
if os.path.exists(file_path):
    # Read the contents of the file
    with open(file_path, 'r') as file:
        logs = file.readlines()
    
    # Define a regular expression pattern to extract the number patterns
    pattern = re.compile(r'Box (\d+,\d+,\d+,\d+):')
    
    # Extract the number patterns from each line
    extracted_patterns = [pattern.search(line).group(1) for line in logs if pattern.search(line)]
    
    # Create a DataFrame from the extracted patterns
    df = pd.DataFrame(extracted_patterns, columns=['bounding_box'])
    
else:
    print(f"The file {file_path} does not exist.")

bbox_sample = df['bounding_box'].sample(100).tolist()

building_plans.scrape_in_batches(bbox_sample,
                      batch_size = 100,
                      batch_delay = 30, 
                      max_retries = 5,
                      output_folder = 'data/raw/geoservices_results_errors_sample')