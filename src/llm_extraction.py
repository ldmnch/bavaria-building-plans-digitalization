# %%
import os
import base64
import pandas as pd
import asyncio
import tiktoken
import time
import re
import json
import asyncio
import nest_asyncio

from datetime import datetime
from dotenv import load_dotenv
from openai import RateLimitError, APIStatusError
from llama_index.llms.azure_openai import AzureOpenAI

from llama_index.core import (
    PromptTemplate
)
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.query_pipeline import QueryPipeline, FnComponent
from mimetypes import guess_type
from pydantic import BaseModel, Field, conint, confloat
from llama_index.core.output_parsers import PydanticOutputParser

from typing import List, Optional, Literal

from dataclasses import dataclass, field

from helpers.helpers import read_json_to_str

# %%
# Option 1: Use httpimport to load 'azure_authentication' package remotely from GitHub without installing it
import httpimport
with httpimport.remote_repo('https://raw.githubusercontent.com/soda-lmu/azure-auth-helper-python/main/src'
                            '/azure_authentication/'):
    from customized_azure_login import CredentialFactory

# %% [markdown]
# To do:
# 
# - Improve prompt.
# - Run on all images.

# %%
os.chdir("../")
CWD = os.getcwd()

data_dir = os.path.join(CWD, 'data')

#Specify mode (working with a sample or all the files?)
sample_mode = True 
sample_size = 50

# specify file path
INPUT_FILE_PATH = os.path.join(CWD, "data", "proc", "building_plans_sample", "test_images", "bp_text.json")
METADATA_PATH = os.path.join(CWD, "data", "proc", "building_plans", "metadata","building_plans_metadata.csv")

# specify relevant column names
ID_COLUMN='filename'
TEXT_COLUMN='content'

# read in data
bp_text = pd.read_json(INPUT_FILE_PATH)
metadata_df = pd.read_csv(METADATA_PATH)

# %%
metadata_bps = metadata_df[metadata_df['Planart'].isin(['qualifizierter Bebauungsplan', 'einfacher Bebauungsplan', 'vorhabenbezogener Bebauungsplan'])]

# %%
bp_text['id'] = bp_text['filename'].str.extract(r'(\d+)_').astype(int)

# %%
#input_df = metadata_bps.merge(bp_text)

# %%
input_df = bp_text

# %%
# Recommendation: Configure your own authentication workflow with environment variables, see the description at
# https://github.com/soda-lmu/azure-auth-helper-python/blob/main/AuthenticationWorkflowSetup.md
credential = CredentialFactory().select_credential()
token_provider = credential.get_login_token_to_azure_cognitive_services()

print("Instantiate Azure OpenAI Client")

# %%
llm4 = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_ENDPOINT_GIST_PROJECT_NORWAYEAST"],
    engine="gpt-4-1106-preview", 
    model="gpt-4-1106-preview",
    api_key=token_provider(),
    api_version="2024-02-01",  
    timeout=600.0,  # throw APITimeoutError after 10 minutes without a response (default behavior)
)



# %%
os.getcwd()

# %%
class GRZ(BaseModel):
    value: Optional[float] = Field(
        None,
        description="Der numerische Wert der Grundflächenzahl oder 'null', falls nicht vorhanden.",
        example=0.75
    )

class GFZ(BaseModel):
    value: Optional[float] = Field(
        None,
        description="Der numerische Wert der Geschoßflächenzahl oder 'null', falls nicht vorhanden.",
        example=1.0
    )

class BuildingMetrics(BaseModel):
    
    grz: Optional[GRZ] = Field(None, description="Grundflächenzahl (GRZ)")
    
    gfz: Optional[GFZ] = Field(None, description="Geschoßflächenzahl (GFZ)")
    
class PromptRoleAndTask:
    """Describes LLM role and task for prompt."""

    role: str = "You are a helpful enviromental city planner. \n Based on the excerpt from a building plan provided below, we would like to extract following information.\n"

class PromptKpiDefinitions:
    """Provides definitions to each KPI in prompt."""

    definitions_string : str = read_json_to_str('./query/definitions.json')


# %%
@dataclass
class Llm_Extraction_Prompt:
    """
    The dataclass contains a prompt (=query text).
    Strategy: We make a single query to extract relevant info from BP.
    """

    """The dataclass contains a prompt (=query text) and a parser method for this prompt.
        Strategy: We make a single query to extract relevant info from BP.
"""

    role: Optional[str] = field(default=PromptRoleAndTask.role)
    KPIDefinitions: Optional[str] = field(default=PromptKpiDefinitions().definitions_string)
    #specifications: Optional[str] = field(default=prompt_specifications.specifications)

    def __init__(self, role=None, KPIDefinitions=None#, specifications=None
                 ):
        """Optional parameters allow default values to be loaded from a file if None is provided."""
        if role is None:
            role = PromptRoleAndTask.role  # Default role definition
        if KPIDefinitions is None:
            KPIDefinitions = PromptKpiDefinitions().definitions_string  # Default KPI definitions
#        if specifications is None:
#            specifications = prompt_specifications.specifications  # Default specifications

        self.query = f'{role}\n{KPIDefinitions}\n\
        Here is the excerpt: \n {{context_str}}'

        self.parser = PydanticOutputParser(output_cls=BuildingMetrics)

    @staticmethod
    def parse_gpt_output(self, gpt_question_output) -> pd.DataFrame:
        """Extract year, scope, value, and unit gpt_question_output using regular expressions."""

        building_metrics = self.parser.parse(gpt_question_output.message.content)

        parsed_output = pd.DataFrame([entry.dict()
                                     for entry in building_metrics.BuildingMetrics])

        return(parsed_output)


# %%
class BP_Metrics_Getter:
    """Retrieve emissions from a single document."""

    def __init__(self, llm, llm_single_prompt, start_time: float):
        self.llamaindex_llm = llm.llamaindex_llm
        self.llm_semaphore = llm.semaphore
        self.token_counter = llm.token_counter
        self.llm_single_prompt = llm_single_prompt
        self.start_time = start_time

    async def _bound_get_values_from_raw_text(self, doc_text):
        """Getter function with semaphore."""

        async with self.llm_semaphore:
            current_time = datetime.now()
            cur_time = time.perf_counter()
            elapsed_time = cur_time - self.start_time
            print("Current Time:", current_time.strftime("%H:%M:%S"), "(", elapsed_time / 60,
                  "minutes since process started.)")
            
            res = await self._run_llm(doc_text)

            duration_time = time.perf_counter() - cur_time
            total_duration_time = time.perf_counter() - self.start_time
            print("LLM query execution time: " + str(duration_time) + " seconds (" +
                  str(total_duration_time) + " seconds since initiating ValueRetrieverPipeline).")
        return res

    async def _run_llm(self, doc_text: str):
        """Extract emissions from a single page of a document.

        Example code to extract emissions from a single PDF document

        embed_model = config.EmbeddingModel().embed_model
        llm = config.Llm(model_name="gpt-35-turbo-16k")
        llm_single_prompt = prompts_with_prompt_parsers.LlmSinglePromptQueryScope123()
        start_time = time.perf_counter()
        emission_getter = EmissionsGetter(
            llm=llm, llm_single_prompt=llm_single_prompt, start_time=start_time)

        pathname_list = glob.glob(os.path.join(
            path_to_data, "input-data/*.pdf"))
        doc = semantic_search.Pdfdoc(filename=filename)
        relevant_pages = doc.retrieve_relevant_pages(embed_model)

        output = await asyncio.gather(*(emission_getter.get_emissions_from_raw_text(doc_text=page.text) for page in relevant_pages))
        """

        prompt = self.llm_single_prompt.query
        parsing_instruction = self.llm_single_prompt.parser
        prompt_tmpl = PromptTemplate(template=f"{prompt}",
                                     output_parser=parsing_instruction)

        p = QueryPipeline(modules={"llm_prompt": prompt_tmpl,
                                   "llm": self.llamaindex_llm},
                          verbose=False)
        p.add_chain(["llm_prompt", "llm"])

        try:
            
            results = await p.arun_multi({"llm_prompt": {"context_str": doc_text}},
                                         CallbackManager([self.token_counter]))
            
            raw_response = results["llm"]["output"]

        except RateLimitError as e:
            print(
                "A 429 status code (Rate Limit error) was received; we should back off a bit.")
            raw_response = "Create empty output table"

        except APIStatusError as e:

            raw_response = "Create empty output table"

            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)

        return raw_response
    
    def _parse_to_table_llm_output(self, llm_output):

        output_string = str(llm_output)

        parsed_output = self.llm_single_prompt.parse_gpt_output(output_string)

        return parsed_output

    def _parse_to_classes_llm_output(self, llm_output):

        parsed_output = self.llm_single_prompt.parse_gpt_output(llm_output)

        return parsed_output


# %%

async def extract_bp_info(prompt_selected,
                    data):
    
    p = _run_llm(prompt_selected)

    results = []

    for index, row in data.iterrows():
        
        res = await run_pipeline_on_rows(row['content'], p)
        table_output = res['output_parser']['res']
        table_output['id'] = row['id']
        table_output['filename'] = row['filename']
        results.append(table_output)

    return(results)

# %%
run_data = input_df

# %%
nest_asyncio.apply()

#flooding_results = await extract_bp_info(Llm_Flooding_Prompt(), run_data)
extraction_results = await extract_bp_info(Llm_Extraction_Prompt(), run_data)

# %%
extraction_results

# %%
extraction_df = pd.concat(extraction_results)
#flooding_df = pd.concat(flooding_results)

# %%
OUTPUT_FLOODING_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "test_images_flooding_data_extraction.csv")
OUTPUT_EXTRACTIONS_FILE_PATH = os.path.join("data", "proc", "building_plans_sample", "features",  "test_images_info_data_extraction.csv")


extraction_df.to_csv(OUTPUT_EXTRACTIONS_FILE_PATH)
flooding_df.to_csv(OUTPUT_FLOODING_FILE_PATH)


