import os
import base64
import pandas as pd
import nest_asyncio
import asyncio

from azure_authentication.customized_azure_login import CredentialFactory

from textual_features.agent_extraction import Llm, BP_Metrics_Getter
from textual_features.prompts_and_parsers import Llm_Extraction_Prompt
from textual_features.extraction_pipeline import Pipeline

CWD = os.getcwd()

data_dir = os.path.join(CWD, 'data')

#Specify mode (working with a sample or all the files?)
sample_mode = False 
sample_size = 50

# specify file path
INPUT_FILE_PATH = os.path.join(data_dir, "proc", "building_plans_sample", "test_images", "bp_text.json")

PROMPT_TYPE = 'sealing' # Can be sealing, floors or flooding depending on the prompt you want to use

if PROMPT_TYPE == 'sealing':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "test_images_info_data_extraction.csv")
if PROMPT_TYPE == 'flooding':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "test_images_info_data_extraction_flooding.csv")
if PROMPT_TYPE == 'floors':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "test_images_info_data_extraction_floors.csv")

ID_COLUMN='filename'
TEXT_COLUMN='content'

# read in data
bp_text = pd.read_json(INPUT_FILE_PATH)

bp_text['id'] = bp_text['filename'].str.extract(r'(\d+)_').astype(int)

input_df = bp_text

credential = CredentialFactory().select_credential()
token_provider = credential.get_login_token_to_azure_cognitive_services()

if sample_mode:
    
    run_data = input_df.sample(sample_size, random_state=15)

else: 
 
    run_data = input_df

llm = Llm(model_name="gpt-4-1106-preview")
getter = BP_Metrics_Getter(llm = llm, llm_single_prompt = Llm_Extraction_Prompt(prompt_type = PROMPT_TYPE))

# Run the async function properly
if __name__ == "__main__":
    results = asyncio.run(Pipeline.run_llm_extraction(data = run_data, getter = getter, llm = llm)) 
    print(results)  
    Pipeline.save_llm_extraction_results(results, OUTPUT_FILE_PATH)