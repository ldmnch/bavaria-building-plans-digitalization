import pandas as pd
import os 
from evaluation.extraction_pipeline_evaluation import EvaluationPipeline


if __name__ == "__main__":

    CWD = os.getcwd()

    # Define paths to the ground truth and newly extracted data
    newly_extracted_data_path = os.path.join("data", "proc", "building_plans_sample", "features",  "info_data_extraction_new.csv")
    ground_truth_path = os.path.join("data", "final", "tables", "annotations",  "filled")

    # Create an instance of the EvaluationPipeline class
    evaluation_pipeline = EvaluationPipeline(ground_truth_path, newly_extracted_data_path)

    # Run the evaluation pipeline
    f1, accuracy, row_errors = evaluation_pipeline.run()

    # Print the results
    print(f1, accuracy)