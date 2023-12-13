import random

def generate_ranges(bbox = (4195669.333333333, 4998144, 4724053.333333333, 5766144)):
    '''
    Takes as input coordinates of a bounding box and yields all combinations of 1000x1000 ranges within that box. 

    Arguments:
        bbox : a series of coordinates in a tuple. 

    Returns:
        Generator object with sub-boxes. 
    '''
    min_x, min_y, max_x, max_y = bbox
    step = 1000
    
    for x in range(int(min_x), int(max_x), step):
        for y in range(int(min_y), int(max_y), step):
            x_end = min(x + step, int(max_x))
            y_end = min(y + step, int(max_y))
            yield (x, y, x_end, y_end)

def generate_sub_bboxes(sample_n = False,
                        bounding_box = (4195669.333333333, 4998144, 4724053.333333333, 5766144)):
    
    '''
    Runs generate_ranges() function on a specified bounding box and appends new sub-bboxes as string to a list. 

    Arguments:
        bounding_box : bounding box in string format. 
        sample_n : integer with N for sample. If it is not defined, it returns all bounding boxes

    Returns: 
    
        boxes : list of sub-bounding boxes. 
    '''

    boxes = []

    for sub_bbox in generate_ranges(bounding_box):
        boxes.append(sub_bbox)

    boxes = [",".join(map(str, b)) for b in boxes]

    if sample_n:

        random.seed(12)

        boxes = random.sample(boxes, sample_n)

    return(boxes)