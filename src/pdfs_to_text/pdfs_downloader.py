import os
import pandas as pd
import asyncio
import aiohttp
import numpy as np
import shutil
from pathlib import Path
from aiohttp import ClientSession
from tqdm.asyncio import tqdm

class PdfDownloader: 

    def __init__(self, input_df, id_column, link_column, output_folder, 
                 sample, batch_size, blob_service_client, azure_container, 
                 azure_upload_blob):
        self.input_df = input_df
        self.id_column = id_column
        self.link_column = link_column
        self.output_folder = output_folder
        self.sample = sample
        self.batch_size = batch_size
        self.blob_service_client = blob_service_client
        self.azure_container = azure_container
        self.azure_upload_blob = azure_upload_blob

    async def is_downloadable(self, url: str, session: ClientSession) -> bool:
        """Check if the URL contains downloadable content."""
        try:
            async with session.head(url) as response:
                return 'Content-Disposition' in response.headers or 'application/pdf' in response.headers.get('Content-Type', '')
        except Exception:
            return False

    async def download_pdf(self, session, link, object_id, output_folder, timeout_seconds=120):
        """Asynchronously download a PDF and save it to the output folder."""
        error = None
        try:
            if await self.is_downloadable(link, session):
                # Attempt to fetch the PDF
                async with session.get(link, timeout=timeout_seconds) as response:
                    if response.status == 200:
                        pdf_name = f"{object_id}.pdf"
                        pdf_path = os.path.join(output_folder, pdf_name)
                        with open(pdf_path, 'wb') as pdf_file:
                            pdf_file.write(await response.read())
                    else:
                        error = (link, object_id)
            else:
                error = (link, object_id)

        except Exception:
            error = (link, object_id)

        return error

    async def process_group(self, session, group, id_column, link_column, output_folder):
        """Process one group of data and attempt to download PDFs."""
        error_links = []
        error_ids = []
        
        for _, row in group.iterrows():
            link = row[link_column]
            object_id = str(row[id_column])

            error = await self.download_pdf(session, link, object_id, output_folder)
            
            if not error:
                break
            else:
                error_links.append(error[0])
                error_ids.append(error[1])

        return error_links, error_ids

    async def run_pdf_downloader_async(
            self, 
            input_df: pd.DataFrame,
            id_column: str,
            link_column: str,
            output_folder: str,
            sample: bool = False
    ):
        """Asynchronous function to download PDFs from a DataFrame."""
        
        error_links = []
        error_ids = []

        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        if sample:
            input_df = self.input_df.groupby(['bplan_date_category', 'flooding_risk', 'ROR']).apply(
                lambda x: x.sample(min(len(x), 10))
            ).reset_index(drop=True)

        async with aiohttp.ClientSession() as session:
            tasks = []
            grouped = input_df.groupby(['bplan_date_category', 'flooding_risk', 'ROR'])
            
            for _, group in grouped:
                tasks.append(self.process_group(session, group, id_column, link_column, output_folder))
            
            results = await asyncio.gather(*tasks)

            for group_errors in results:
                if group_errors:
                    group_error_links, group_error_ids = group_errors
                    error_links.extend(group_error_links)
                    error_ids.extend(group_error_ids)

        errors_df = pd.DataFrame({'objectid': error_ids, 'scanurl': error_links})
        errors_df.to_csv(os.path.join(output_folder, "error_links.csv"), index=False)

    async def process_batches_async(self, input_batches):
        """Process batches asynchronously without calling asyncio.run() repeatedly."""
        for batch_idx, batch in enumerate(input_batches):
            print(f"Processing batch {batch_idx + 1} of {len(input_batches)}...")

            batch_name =  f"batch-{batch_idx + 1}"

            batch_folder = os.path.join(self.output_folder , batch_name)

            if os.path.isdir(batch_folder):
                print("existing folder")
            else:
                os.mkdir(batch_folder)

            
            await self.run_pdf_downloader_async(batch, 
                                                self.id_column, 
                                                self.link_column, 
                                                str(batch_folder), 
                                                self.sample)

            # Use the injected Azure upload function
            self.azure_upload_blob(self.azure_container(self.blob_service_client, batch_name), str(batch_folder))

            shutil.rmtree(batch_folder) 


    def run_batch_pdf_downloader(self):
        """
        Wrapper function to run the asyncio-based downloader in a blocking context efficiently.
        """

        if self.batch_size:

            input_batches = np.array_split(self.input_df, len(self.input_df) // self.batch_size)
            asyncio.run(self.process_batches_async(input_batches))  # Efficient event loop handling

        else:
            asyncio.run(self.run_pdf_downloader_async(self.input_df))

            container_client = self.azure_container(str(self.output_folder))

            # Use the injected Azure upload function
            self.azure_upload_blob(container_client, str(self.output_folder))
