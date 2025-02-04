import os
import base64
import pandas as pd
import nest_asyncio
import asyncio

from azure_authentication.customized_azure_login import CredentialFactory

from textual_features.agent_extraction import Llm, BP_Metrics_Getter
from textual_features.prompts_and_parsers import Llm_Extraction_Prompt
from textual_features.extraction_pipeline import Pipeline

def create_llm_costs_dict(response):
    
    """Creates a dictionary with the costs of the LLM."""

    response_usage = response.raw.usage
    
    llm_costs = {
        "llm_prompt_tokens": response_usage.prompt_tokens,
        "llm_completion_tokens": response_usage.completion_tokens,
        "total_llm_token_count": response_usage.total_tokens,
        "total_llm_costs_in_euro": llm.calculate_llm_calling_price(response_usage.prompt_tokens,
                                                                   response_usage.completion_tokens),
    }

    return llm_costs

CWD = os.getcwd()

data_dir = os.path.join(CWD, 'data')

#Specify mode (working with a sample or all the files?)
sample_mode = False 
sample_size = 50

# specify file path
INPUT_FILE_PATH = os.path.join(data_dir, "proc", "building_plans_sample", "test_images", "bp_text.json")
METADATA_PATH = os.path.join(data_dir, "proc", "building_plans", "metadata","building_plans_metadata.csv")

#Specify prompt extraction + output file path
PROMPT_TYPE = 'flooding'

if PROMPT_TYPE == 'construction':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "test_images_info_data_extraction.csv")
if PROMPT_TYPE == 'flooding':
    OUTPUT_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "test_images_info_data_extraction_flooding.csv")

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