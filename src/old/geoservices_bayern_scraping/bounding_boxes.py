def split_bounding_box_with_custom_midpoint(bbox, x_splits=2, y_splits=2):
    """
    This function takes a bounding box and splits it into smaller sub-bounding boxes.
    It returns the sub-bounding boxes and their respective midpoints, with midpoints in the
    same format as the provided example (easting, northing).

    Args:
    - bbox (list or tuple): A bounding box defined as [xmin, ymin, xmax, ymax]
    - x_splits (int): The number of splits along the x-axis (default is 2)
    - y_splits (int): The number of splits along the y-axis (default is 2)

    Returns:
    - sub_bboxes (list): A list of sub-bounding boxes in the form [xmin, ymin, xmax, ymax]
    - midpoints (list): A list of midpoints in the form {"easting": x, "northing": y}
    """
    xmin, ymin, xmax, ymax = bbox

    # Calculate the width and height of each split
    x_step = (xmax - xmin) / x_splits
    y_step = (ymax - ymin) / y_splits

    # Generate sub-bounding boxes by iterating through the splits
    sub_bboxes = []
    for i in range(x_splits):
        for j in range(y_splits):
            sub_xmin = xmin + i * x_step
            sub_ymin = ymin + j * y_step
            sub_xmax = sub_xmin + x_step
            sub_ymax = sub_ymin + y_step
            sub_bboxes.append([sub_xmin, sub_ymin, sub_xmax, sub_ymax])

    # Calculate the midpoints of each sub-bounding box
    midpoints = []
    for sub_bbox in sub_bboxes:
        sub_xmin, sub_ymin, sub_xmax, sub_ymax = sub_bbox
        sub_mid_x = (sub_xmin + sub_xmax) / 2
        sub_mid_y = (sub_ymin + sub_ymax) / 2
        # Store midpoints as easting and northing
        midpoints.append({"easting": sub_mid_x, "northing": sub_mid_y})

    return sub_bboxes, midpoints

# Example usage
bbox = [704941.75, 5406403.42, 714583.45, 5419583.59]

# Goal midpoints to check against
goal_midpoint = {"easting": 4503718.338133049, "northing": 5407116.539337536}
x_range = 2
y_range = 2
# Now we use a while loop to adjust x_range and y_range until we reach the goal midpoint
while True: 
    sub_bboxes, midpoints = split_bounding_box_with_custom_midpoint(bbox, x_range, y_range)

    # Check if any of the sub-bounding boxes' midpoints match the goal
    match_found = False
    for midpoint in midpoints:
        if (midpoint["easting"] < goal_midpoint["easting"] and 
            midpoint["northing"] < goal_midpoint["northing"]):
            match_found = True
            break
    
    # If a match is found, exit the loop
    if match_found:
        break
    else: 
        y_range += 1  # Increment y_range
        x_range += 1  # Increment x_range

# Final x_range, y_range, and midpoints when the goal is reached
print(f"Final x_range: {x_range}, y_range: {y_range}")
print(f"Midpoints: {midpoints}")


# Do inverse calculations for midpoints of the bounding boxes