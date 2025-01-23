import pandas as pd
import geopandas as gpd
from geoservices_bayern_scraping import building_plans
from geoservices_bayern_scraping import helpers_geoservices_scraping

gemeinden = gpd.read_file('./data/raw/bavaria_regions/bav_mun_GK4_prj.shp')
# Get the bounding box for each polygon (returns a tuple: minx, miny, maxx, maxy)
gemeinden[['minx', 'miny', 'maxx', 'maxy']] = gemeinden.geometry.bounds

# Now you can calculate width and height
gemeinden['width'] = gemeinden['maxx'] - gemeinden['minx']
gemeinden['height'] = gemeinden['maxy'] - gemeinden['miny']

# Calculate midpoint
gemeinden['midpoint_x'] = (gemeinden['minx'] + gemeinden['maxx']) / 2
gemeinden['midpoint_y'] = (gemeinden['miny'] + gemeinden['maxy']) / 2

# Optionally, create a Point geometry for the midpoint
from shapely.geometry import Point
gemeinden['midpoints'] = gemeinden.apply(lambda row: Point(row['midpoint_x'], row['midpoint_y']), axis=1)


# Extract easting and northing from the midpoint
gemeinden['easting'] = gemeinden['midpoints'].apply(lambda x: x.y)
gemeinden['northing'] = gemeinden['midpoints'].apply(lambda x: x.x)
#
example = gemeinden[gemeinden['gem_name'].str.contains('Herrngiersdorf',case=False, na=False)]

building_plans.scrape_in_batches(example,
# Calculate the midpoint of each polygon (midpoint of the bounding box)
                      batch_size = 100,
                      batch_delay = 30, 
                      max_retries = 3,
                      output_folder = './data/raw/geoservices_results_sample', 
                      size_n = None)

