import os
import base64
import pandas as pd

from helpers.helpers import create_llm_costs_dict
from azure_authentication.customized_azure_login import CredentialFactory

import nest_asyncio
import asyncio

class Pipeline:
    """
    _summary_
    """
    async def run_and_save_llm_extraction(data, getter, llm, output_path):
        results = await run_llm_extraction(data, getter, llm)
        save_llm_extraction_results(results, output_path)

    async def run_llm_extraction(data, getter, llm):
        results = []
        
        for i, row in data.iterrows():
            extraction_results = await getter._bound_get_emissions_from_raw_text(row['content'])
            llm_costs = create_llm_costs_dict(extraction_results, llm)
            llm.token_counter.reset_counts()

            parsed_extractions = getter._parse_to_table_llm_output(extraction_results)        
            
            row_data = {
                "id": row.get("id", None),  
                "filename": row.get("filename", None),
                "llm_prompt_tokens": llm_costs["llm_prompt_tokens"],
                "llm_completion_tokens": llm_costs["llm_completion_tokens"],
                "total_llm_token_count": llm_costs["total_llm_token_count"],
                "total_llm_costs_in_euro": llm_costs["total_llm_costs_in_euro"]
            }
            
            row_data.update(parsed_extractions)
            results.append(row_data)
        
        return results

    def save_llm_extraction_results(results, output_path):
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_path, index=False)