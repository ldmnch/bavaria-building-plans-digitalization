import pandas as pd
from geoservices_bayern_scraping import building_plans, bounding_boxes

gemeinden = pd.read_json('./data/proc/geobayern_bpsites/geobayern_bauleitsites.json', orient= "index")

building_plans.scrape_in_batches(gemeinden,
                      batch_size = 100,
                      batch_delay = 30, 
                      max_retries = 3,
                      output_folder = './data/raw/geoservices_results')