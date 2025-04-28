import pandas as pd
import os
import glob
import numpy as np

class EvaluationPipeline:

    def __init__(self, ground_truth_path, newly_extracted_data_path, evaluation_mode):
        self.ground_truth_path = ground_truth_path
        self.newly_extracted_data_path = newly_extracted_data_path
        self.evaluation_mode = evaluation_mode

    def run(self):
        # Import and preprocess the data
        ground_truth_data = self.import_and_prepro_ground_truth(self.ground_truth_path)

        if self.evaluation_mode == 'ground_truth':

            # Get results at document level
            df = self.get_type_of_error_at_row_level(ground_truth_data, evaluation_mode=self.evaluation_mode)
            
            row_errors = df.groupby(['met', 'correct_result']).size().reset_index(name='count')
            # Get f1 score and accuracy for each metric
            metrics = row_errors['met'].unique()
            f1_scores = self.compute_f1_score_per_metric(row_errors, metrics)
            accuracies = self.compute_accuracy_per_metric(row_errors, metrics)

        if self.evaluation_mode == 'new_data':

            newly_extracted_data = self.import_and_prepro_new_data(self.newly_extracted_data_path)

            # Join the newly extracted data with the ground truth data
            df = self.join_with_ground_truth(newly_extracted_data, ground_truth_data)

            # Get results at row level
            row_errors = self.get_type_of_error_at_row_level(df, evaluation_mode=self.evaluation_mode)
            row_errors = row_errors.groupby(['met', 'correct_result']).size().reset_index(name='count')

            # Get f1 score and accuracy for each metric
            metrics = row_errors['met'].unique()
            f1_scores = self.compute_f1_score_per_metric(row_errors, metrics)
            accuracies = self.compute_accuracy_per_metric(row_errors, metrics)
            
        return f1_scores, accuracies, row_errors
    
    def import_and_prepro_ground_truth(self, path : str):

        #must be path to folder with xlsx files of annotation

        all_files =  all_files = glob.glob(os.path.join(path, "*.xlsx"))
 

        df_from_each_file = (pd.read_excel(f, skiprows = 3) for f in all_files)
        df = pd.concat(df_from_each_file, ignore_index=True)

        df.dropna(subset=['id'], inplace=True)

        # Keeping only evaluation of existing rows 

        df['id'] = df['id'].astype(str)
        df['id_general'] = df['id'].str.replace(r'X_', '', regex=True)
        # Convert id general to numeric, errors='coerce' will convert non-numeric values to NaN
        df['id_general'] = pd.to_numeric(df['id_general'], errors='coerce')

        return df


    def import_and_prepro_new_data(self, path : str): 
        """
        Import and preprocess new data from a CSV file.
        """
        # Read the CSV file
        newly_extracted_data = pd.read_csv(path)

        newly_extracted_data = newly_extracted_data[['id', 'filename', 'gfz_value', 'grz_value']]

        newly_extracted_data = newly_extracted_data.melt(id_vars=['id', 'filename'], value_vars=['gfz_value', 'grz_value'], var_name='met', value_name='new_value')

        return newly_extracted_data

    def join_with_ground_truth(self, newly_extracted_data, ground_truth_data):
        """
        Join the newly extracted data with the ground truth data.
        """
        df = pd.merge(newly_extracted_data, 
                    ground_truth_data[['id_general','filename', 'met', 'value', 'Wert korrekt? (Ja/ Nein)','Korrigierte Wert (falls nötig)']],
                    left_on=['filename', 'met'], right_on=['filename', 'met'], how='inner')

        # Convert both columns to float for numerical comparison
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['new_value'] = pd.to_numeric(df['new_value'], errors='coerce')

        # For equality comparison, consider a small tolerance for floating-point numbers
        df['match_with_original_value'] = (
            (df['value'].round(6) == df['new_value'].round(6)) | 
            (df['value'].isna() & df['new_value'].isna())
        )

        df['corrected_float'] = pd.to_numeric(df['Korrigierte Wert (falls nötig)'], errors='coerce')
        df['match_with_corrected_value'] = (
            (df['corrected_float'].round(6) == df['new_value'].round(6)) | 
            (df['Korrigierte Wert (falls nötig)'].isna() & df['new_value'].isna())
        )

        return df

    def get_type_of_error_at_row_level(self, df, evaluation_mode='new_data'):
        """
        Determine the type of error based on the comparison of values.
        """

        if evaluation_mode == 'ground_truth':

            df['correct_result'] = np.select(
                [
                    df['Wert korrekt? (Ja/ Nein)'] == 'Ja',
                    (df['Wert korrekt? (Ja/ Nein)'] == 'Nein') & (df['value'].isna()),
                    (df['Wert korrekt? (Ja/ Nein)'] == 'Nein') & (df['value'].notna()),
                    (df['Wert korrekt? (Ja/ Nein)'].isna()) & (df['value'].isna())
                ],
                [
                    'True positive', 
                    'False negative', 
                    'False positive', 
                    'True negative'
                ],
                default=None
            )

        elif evaluation_mode == 'new_data':

            df['correct_result'] = np.select(
                [
                    # True positive: new_value matches the appropriate reference value
                    # Case 1: Original value is correct (Ja) and new_value matches it
                    ((df['Wert korrekt? (Ja/ Nein)'] == 'Ja') & df['match_with_original_value']),
                    # Case 2: Original value is incorrect (Nein) and new_value matches the corrected value
                    ((df['Wert korrekt? (Ja/ Nein)'] == 'Nein') & df['match_with_corrected_value']),
                    
                    # False negative: new_value is missing but should exist
                    (df['new_value'].isna() & 
                    ((df['Wert korrekt? (Ja/ Nein)'] == 'Ja') | 
                    ((df['Wert korrekt? (Ja/ Nein)'] == 'Nein').values & df['Korrigierte Wert (falls nötig)'].notna().values))),
                    
                    # False positive: new_value exists but doesn't match the appropriate reference value
                    # Case 1: Original value is correct (Ja) but new_value doesn't match
                    ((df['Wert korrekt? (Ja/ Nein)'] == 'Ja') & df['new_value'].notna() & (~df['match_with_original_value'])),
                    # Case 2: Original value is incorrect (Nein) and new_value doesn't match correction
                    ((df['Wert korrekt? (Ja/ Nein)'] == 'Nein') & df['new_value'].notna() & (~df['match_with_corrected_value'])),
                    
                    # True negative: nothing to extract and nothing was extracted
                    (df['new_value'].isna() & 
                    ((df['Wert korrekt? (Ja/ Nein)'].isna()) | 
                    ((df['Wert korrekt? (Ja/ Nein)'] == 'Nein').values & df['Korrigierte Wert (falls nötig)'].isna().values)))
                ],
                [
                    'True positive',
                    'True positive',
                    'False negative', 
                    'False positive',
                    'False positive',
                    'True negative'
                ],
                default=None
            )    

        return df
                
    def compute_f1_score(self, df, metric):
        """
        Computes the F1 score for a given metric based on the evaluation results.

        Args:
        df (pd.DataFrame): The input DataFrame.
        metric (str): The metric for which to compute the F1 score.

        Returns:
        float: The F1 score for the given metric.
        """
        # Extract relevant rows for the specified metric
        metric_data = df[df['met'] == metric]

        # Extract counts for True Positives, False Positives, and False Negatives
        tp = metric_data[metric_data['correct_result'] == 'True positive']['count'].sum()
        fp = metric_data[metric_data['correct_result'] == 'False positive']['count'].sum()
        fn = metric_data[metric_data['correct_result'] == 'False negative']['count'].sum()

        # Compute precision and recall
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        # Compute F1 score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return f1_score

    def compute_f1_score_per_metric(self, df, metrics):

        """
        Computes the F1 score for each metric in the DataFrame.

        Args:
        df (pd.DataFrame): The input DataFrame.
        metrics (list): List of metrics to compute F1 scores for.

        Returns:
        pd.DataFrame: A DataFrame with metrics and their corresponding F1 scores.
        """
        f1_scores = []

        for metric in metrics:
            f1_score = self.compute_f1_score(df, metric)
            f1_scores.append({'metric': metric, 'f1_score': f1_score})

        return pd.DataFrame(f1_scores)

    def compute_accuracy(self, df, metric):
        """
        Computes the accuracy for a given metric based on the evaluation results.

        Args:
        df (pd.DataFrame): The input DataFrame.
        metric (str): The metric for which to compute the accuracy.

        Returns:
        float: The accuracy for the given metric.
        """
        # Extract relevant rows for the specified metric
        metric_data = df[df['met'] == metric]

        # Extract counts for True Positives and True Negatives
        tp = metric_data[metric_data['correct_result'] == 'True positive']['count'].sum()
        tn = metric_data[metric_data['correct_result'] == 'True negative']['count'].sum()
        total = metric_data['count'].sum()

        # Compute accuracy
        accuracy = (tp + tn) / total if total > 0 else 0

        return accuracy
    
    def compute_accuracy_per_metric(self, df, metrics):

        """
        Computes the accuracy for each metric in the DataFrame.

        Args:
        df (pd.DataFrame): The input DataFrame.
        metrics (list): List of metrics to compute accuracies for.

        Returns:
        pd.DataFrame: A DataFrame with metrics and their corresponding accuracies.
        """
        accuracies = []

        for metric in metrics:
            accuracy = self.compute_accuracy(df, metric)
            accuracies.append({'metric': metric, 'accuracy': accuracy})

        return pd.DataFrame(accuracies)
