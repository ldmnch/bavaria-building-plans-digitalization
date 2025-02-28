import os
import base64
import pandas as pd
import nest_asyncio
import asyncio
import random 

from azure_authentication.customized_azure_login import CredentialFactory

from textual_features.agent_extraction import Llm, BP_Metrics_Getter
from textual_features.prompts_and_parsers import Llm_Extraction_Prompt
from textual_features.extraction_pipeline import Pipeline

CWD = os.getcwd()

data_dir = os.path.join(CWD, 'data')

#Specify mode (working with a sample or all the files?)
sample_mode = False
sample_size = 15

# specify file path
INPUT_FILE_PATH = os.path.join(data_dir, "proc", "building_plans_sample", "bp_text.json")

PROMPT_TYPE = 'flooding' # Can be sealing, floors or flooding depending on the prompt you want to use

if PROMPT_TYPE == 'sealing':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "info_data_extraction.csv")
if PROMPT_TYPE == 'flooding':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "info_data_extraction_flooding.csv")
if PROMPT_TYPE == 'floors':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "info_data_extraction_floors.csv")

ID_COLUMN='filename'
TEXT_COLUMN='content'

# read in data
bp_text = pd.read_json(INPUT_FILE_PATH)

bp_text['id'] = bp_text['filename'].str.extract(r'(\d+)_').astype(int)

input_df = bp_text

if sample_mode:

    random.seed(42)  # Set the random seed for reproducibility
    unique_ids = input_df['id'].unique()
    sample_ids = random.sample(list(unique_ids), sample_size)

    run_data = input_df[input_df['id'].isin(sample_ids)]
else: 
 
    run_data = input_df

llm = Llm(model_name="gpt-4-1106-preview")
getter = BP_Metrics_Getter(llm = llm, llm_single_prompt = Llm_Extraction_Prompt(prompt_type = PROMPT_TYPE))
pipeline_instance = Pipeline()

# Run the async function properly
if __name__ == "__main__":

# Create an instance of the Pipeline class
    # Run the method using an instance of the class
    results = asyncio.run(pipeline_instance.run_and_save_llm_extraction(data=run_data, getter=getter,
                                                                        llm=llm, batch_size=10,
                                                                        output_path=OUTPUT_FILE_PATH))    
    print(results)  
