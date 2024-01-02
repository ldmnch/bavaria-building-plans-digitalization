from src.geoservices_bayern_scraping import building_plans, bounding_boxes

bavaria_bounding_box =  (4195669.333333333, 4998144, 4724053.333333333, 5766144)

bounding_boxes = bounding_boxes.generate_sub_bboxes(bounding_box= bavaria_bounding_box)

#Resume from error point: 

bounding_boxes = bounding_boxes[102759:]

building_plans.scrape_in_batches(bounding_boxes,
                      batch_size = 500,
                      batch_delay = 30, 
                      max_retries = 5,
                      output_folder = 'geoservices_results')
