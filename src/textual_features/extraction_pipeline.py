import os
import base64
import pandas as pd
from aiofiles import open as aio_open


from helpers.helpers import create_llm_costs_dict
from azure_authentication.customized_azure_login import CredentialFactory

import nest_asyncio
import asyncio

class Pipeline:
    """
    _summary_
    """
    #def __init__(self):
    #    pass
        
    async def run_and_save_llm_extraction(self, data, getter, llm, output_path, batch_size=10):
        results = await self.run_llm_extraction(data, getter, llm, batch_size)
        await self.save_llm_extraction_results(results, output_path)

    async def run_llm_extraction(self, data, getter, llm, batch_size=10):
        tasks = []
        results = []
        for i in range(0, len(data), batch_size):
            batch = data.iloc[i:i + batch_size]
            task = asyncio.create_task(self.process_batch(batch, getter, llm))
            tasks.append(task)
        
        completed_tasks = await asyncio.gather(*tasks)

        # Flatten results from all batches
        for task_result in completed_tasks:
            results.extend(task_result)

        return results

    async def process_batch(self, batch_data, getter, llm):
        batch_results = []
        for _, row in batch_data.iterrows():
            try:
                extraction_results = await getter._bound_get_emissions_from_raw_text(row['content'])
            except Exception as e:
                # Log errors or handle them as needed
                print(f"Error processing row: {e}")
                continue
            llm_costs = create_llm_costs_dict(extraction_results, llm)
            llm.token_counter.reset_counts()

            parsed_extractions = getter._parse_to_dict_llm_output(extraction_results)
            row_data = {
                "id": row.get("id", None),
                "filename": row.get("filename", None),
                "llm_prompt_tokens": llm_costs["llm_prompt_tokens"],
                "llm_completion_tokens": llm_costs["llm_completion_tokens"],
                "total_llm_token_count": llm_costs["total_llm_token_count"],
                "total_llm_costs_in_euro": llm_costs["total_llm_costs_in_euro"]
            }
            row_data.update(parsed_extractions)
            batch_results.append(row_data)
        return batch_results

    async def save_llm_extraction_results(self, results, output_path):
        results_df = pd.DataFrame(results)
        async with aio_open(output_path, 'w', newline='') as f:
            await f.write(results_df.to_csv(index=False))

