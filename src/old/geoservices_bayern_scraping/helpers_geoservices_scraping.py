import pandas as pd


def calculate_easting_northing_from_bbox(bbox, num_splits_x=2, num_splits_y=2):
    """
    Calculate the easting and northing range from bounding box and midpoint.
    
    Parameters:
        boundingbox (list): [min_easting, min_northing, max_easting, max_northing].
        midpoint (list): [mid_easting, mid_northing].
    
    Returns:
        dict: A dictionary containing the ranges:
              - "easting_range": (min_easting, max_easting)
              - "northing_range": (min_northing, max_northing)
              - "length": Height of the bounding box (northing range)
              - "width": Width of the bounding box (easting range)
    """
    x_min, y_min, x_max, y_max = bbox
    
    # Calculate width and height of each sub-bounding box
    width = (x_max - x_min) / num_splits_x
    height = (y_max - y_min) / num_splits_y

    sub_bboxes = []
    midpoints = []

    for i in range(num_splits_x):
        for j in range(num_splits_y):
            # Calculate sub-bounding box coordinates
            sub_x_min = x_min + i * width
            sub_y_min = y_min + j * height
            sub_x_max = sub_x_min + width
            sub_y_max = sub_y_min + height
                        
            sub_bboxes.append((sub_x_min, sub_y_min, sub_x_max, sub_y_max))
            midpoints.append((sub_x_min, sub_y_max))

    return midpoints[0], midpoints[1]


def get_easting_northing_from_data(df : pd.DataFrame = './data/proc/geobayern_bpsites/geobayern_bauleitsites.json'): 

    # Apply the function to the DataFrame
    calculated_ranges = df.apply(
        lambda row: calculate_easting_northing_from_bbox(row["boundingbox"]),
        axis=1
    )

    calculated_ranges = pd.DataFrame(calculated_ranges).reset_index().rename(columns={"index":"name", 0: "midpoint"})
    calculated_ranges = calculated_ranges.explode("midpoint").reset_index(drop=True)

    # Bind the calculated ranges to the DataFrame
    calculated_ranges[['easting', 'northing']] = pd.DataFrame(calculated_ranges['midpoint'].tolist(), index=calculated_ranges.index)

    return calculated_ranges
