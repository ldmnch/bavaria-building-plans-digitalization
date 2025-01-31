import os
import logging
import sys
import os.path
import tiktoken
import asyncio

import time

from datetime import datetime
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    PromptTemplate,
    StorageContext,
    load_index_from_storage,
    Settings
)


from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import PromptTemplate
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.query_pipeline import QueryPipeline, FnComponent
from mimetypes import guess_type

from typing import List, Optional, Literal

from dataclasses import dataclass, field

from azure_authentication.customized_azure_login import CredentialFactory


class Llm:
    """

    Contains LLM model

    """

    def __init__(self,
                 model_name="gpt-35-turbo-16k",
                 max_parallel_llm_prompts_running=8):
        
        self.model_name = model_name
        
        credential = CredentialFactory().select_credential()
        token_provider = credential.get_login_token_to_azure_cognitive_services()

        if self.model_name == "gpt-35-turbo-16k":

            self.llamaindex_llm = AzureOpenAI(
                engine="gpt-35-turbo-0301",
                model="gpt-35-turbo-16k",
                temperature=0.0,
                azure_endpoint=os.environ["AZURE_ENDPOINT_GIST_PROJECT_WESTEUROPE"],
                # use_azure_ad=True, # only useful for debugging purposes?
                api_version="2024-02-01",
                api_key=token_provider()
            )

            self.token_counter = TokenCountingHandler(
                # both gpt-3.5-turbo and gpt-4 are based on the same cl100k_base encoding -> doesn't matter which model we use here
                # tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
                tokenizer=tiktoken.encoding_for_model("gpt-4").encode
            )

            self.semaphore = asyncio.Semaphore(
                max_parallel_llm_prompts_running)

        elif self.model_name == "gpt-4-1106-preview":

            self.llamaindex_llm = AzureOpenAI(
                engine="gpt-4-1106-preview", model="gpt-4-1106-preview", temperature=0.0,
                azure_endpoint=os.environ["AZURE_ENDPOINT_GIST_PROJECT_NORWAYEAST"],
                # use_azure_ad=True, # only useful for debugging purposes?
                api_version="2024-02-01",
                api_key=token_provider(),
                max_retries=4,
                timeout=240.0,
                reuse_client=False)

            self.token_counter = TokenCountingHandler(
                # both gpt-3.5-turbo and gpt-4 are based on the same cl100k_base encoding -> doesn't matter which model we use here
                # tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
                tokenizer=tiktoken.encoding_for_model("gpt-4").encode
            )

            self.semaphore = asyncio.Semaphore(
                max_parallel_llm_prompts_running)

        Settings.llm = self.llamaindex_llm

    def calculate_llm_calling_price(self, input_tokens, output_tokens):
        """
        Cost calculator
        based on prices from https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/#pricing
        """

        if self.model_name == "gpt-4-1106-preview":
            return input_tokens / 1000 * 0.010 + output_tokens / 1000 * 0.029
        elif self.model_name == "gpt-35-turbo-16k":
            return input_tokens / 1000 * 0.0005 + output_tokens / 1000 * 0.0015
        else:
            return -1.0

class BP_Metrics_Getter:
    """Retrieve emissions from a single document."""

    def __init__(self, llm, llm_single_prompt):
        self.llamaindex_llm = llm.llamaindex_llm
        self.llm_semaphore = llm.semaphore
        self.token_counter = llm.token_counter
        self.llm_single_prompt = llm_single_prompt
        self.start_time = time.perf_counter()

    async def _bound_get_emissions_from_raw_text(self, doc_text):
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
            results = await p.arun_multi({"llm_prompt": {"context_str": doc_text}})
                                         
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
