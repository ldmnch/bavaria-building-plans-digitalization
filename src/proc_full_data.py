from processing_data import proc_geoservices_results

proc_geoservices_results.generate_dataset_building_plans(
    input_folder_path = './data/raw/geoservices_results',
    output_folder_path = './data/proc/building_plans',
    output_folder_name = 'building_plans_metadata')