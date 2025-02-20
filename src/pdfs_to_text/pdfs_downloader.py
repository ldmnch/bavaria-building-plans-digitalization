import os
from datetime import datetime
import numpy as np
import pandas as pd
import requests
import asyncio
import aiohttp
from aiohttp import ClientSession
import os
import pandas as pd
from tqdm.asyncio import tqdm

async def is_downloadable(url: str, session: ClientSession) -> bool:
    """Check if the URL contains downloadable content."""
    try:
        async with session.head(url) as response:
            return 'Content-Disposition' in response.headers or 'application/pdf' in response.headers.get('Content-Type', '')
    except Exception:
        return False

async def download_pdf(session, link, object_id, output_folder, timeout_seconds=120):
    """Asynchronously download a PDF and save it to the output folder."""
    error = None
    try:
        if await is_downloadable(link, session):
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
        # Catch any exception and append to error
        error = (link, object_id)

    return error


async def process_group(session, group, id_column, link_column, output_folder):
    """Process one group of data and attempt to download PDFs."""
    error_links = []
    error_ids = []
    
    for _, row in group.iterrows():
        link = row[link_column]
        object_id = str(row[id_column])

        # Try downloading
        error = await download_pdf(session, link, object_id, output_folder)
        
        if not error:
            # Successful download; move to the next group
            break
        else:
            # If there’s an error, keep the record
            error_links.append(error[0])
            error_ids.append(error[1])

    return error_links, error_ids


async def run_pdf_downloader_async(
    input_df: pd.DataFrame,
    id_column: str,
    link_column: str,
    output_folder: str,
    sample: bool = False
):
    """Asynchronous function to download PDFs from a DataFrame."""
    
    # Prepare error lists
    error_links = []
    error_ids = []

    # Sample data if specified
    if sample:
        input_df = input_df.groupby(['bplan_date_category', 'flooding_risk', 'ROR']).apply(
            lambda x: x.sample(min(len(x), 10))
        ).reset_index(drop=True)

    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Create a single session for all requests
    async with aiohttp.ClientSession() as session:
        tasks = []
        grouped = input_df.groupby(['bplan_date_category', 'flooding_risk', 'ROR'])
        for (old_bplan, flooding_risk, ROR), group in grouped:
            tasks.append(process_group(session, group, id_column, link_column, output_folder))
        
        # Use asyncio.gather to parallelize the group processing
        results = await tqdm.gather(*tasks, total=len(grouped))

        # Aggregate all errors
        for group_errors in results:
            if group_errors:
                group_error_links, group_error_ids = group_errors
                error_links.extend(group_error_links)
                error_ids.extend(group_error_ids)

    # Save error links to a CSV file
    errors_df = pd.DataFrame({'objectid': error_ids, 'scanurl': error_links})
    errors_df.to_csv(os.path.join(output_folder, "error_links.csv"), index=False)


def run_pdf_downloader(
    input_df: pd.DataFrame,
    id_column: str,
    link_column: str,
    output_folder: str,
    sample: bool = False
):
    """
    Wrapper function to run the asyncio-based downloader in a blocking context.
    """
    asyncio.run(
        run_pdf_downloader_async(input_df, id_column, link_column, output_folder, sample)
    )
