"""
This file provides a mix of helper functions that don't fit well elsewhere.
"""

import asyncio
import itertools
import os.path
import re
import json

import pandas as pd


def remove_decimal_commas_in_numbers(raw_number: str) -> str:
    """Remove commas in numbers (e.g: 53,452,349 -> 53452349)

    It is silently assumed that the fractional part in any number does not have exactly three digits (i.e.,
    53,452,349 != 53452.349)

    Does the function work correctly with numbers having more than 9 digits?
    """

    pattern1 = r'([0-9]{1,3}),([0-9]{3}),([0-9]{3})'
    pattern2 = r'([0-9]{1,3}),([0-9]{3})'

    if (re.search(pattern1, raw_number) != 'None') | (re.search(pattern2, raw_number) != 'None'):
        res = raw_number.replace(",", "")
    else:
        res = raw_number

    return res


def expand_grid(data_dict):
    """
    Create a dataframe from all combinations of provided lists or arrays.

    This function takes a dictionary of lists or arrays and computes the cartesian product of these lists or arrays.
    Each unique combination of elements will form a row in the resulting dataframe. The keys of the dictionary will
    be used as column names in the dataframe.

    Parameters:
    data_dict (dict): A dictionary where keys are column names and values are lists or arrays containing data.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the cartesian product of the provided lists or arrays.

    Example:
        data_dict = {'height': [60, 70], 'weight': [100, 150, 200]}

        expand_grid(data_dict)

       height  weight
    0      60     100
    1      60     150
    2      60     200
    3      70     100
    4      70     150
    5      70     200
    """
    rows = itertools.product(*data_dict.values())
    return pd.DataFrame.from_records(rows, columns=data_dict.keys())


def get_project_directory(path_to_file="src"):
    """
    Problem solved here (poor solution): when using Jupyter Notebooks the working directory is the path of the Jupyter Notebook,
    not the project directory we would like to use.

    See also https://stackoverflow.com/questions/69394705/how-to-set-the-default-working-directory-of-all-jupyter-notebooks-as-the-project

    :param path_to_file: path, where the current file is located
    :return: project directory path
    """

    current_dir = os.getcwd()
    head, tail = os.path.split(current_dir)

    # Is there an automatic way to get the current file name?
    # import ipyparams
    # current_file_name = ipyparams.notebook_name
    # print(current_notebook_name)

    if tail == "src":
        return head
    elif tail == path_to_file:
        return os.path.dirname(os.path.dirname(head))
    else:
        return current_dir


def check_loop():
    """Check if running in Jupyter notebook or not."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():
        return True
    else:
        return False


def read_txt_file(txt_input_path):
    """Read a text file and return its content as a string."""
    with open(txt_input_path, 'r') as file:
        return file.read()


def read_json_to_str(input_json_path):
    """Read a JSON file and return its content as a string."""

    read_definitions = read_txt_file(input_json_path)

    definitions_dict = json.loads(read_definitions)

    definitions_string = ' '.join(definitions_dict.values())

    return definitions_string

def read_output_files(output_path):
    """Read output table file in specified folder."""

    output_file_path = output_path + '03_co2_emission_table2_w_query_responses.csv'

    # Read the output table
    output_table = pd.read_csv(output_file_path)

    return output_table

def update_dataclass(instance, updates):
    """ Update fields of a dataclass instance based on a dictionary. """
    for key, value in updates.items():
        if hasattr(instance, key):
            setattr(instance, key, value)

def list_file_in_folder(folder_path):
    """List output file in the folder."""

    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            return file
