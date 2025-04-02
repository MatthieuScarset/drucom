import re
import sys
import json
import pandas as pd
import asyncio
import aiohttp
import aiofiles
from itertools import islice
import os
import time

BASE_URL = "https://www.drupal.org/api-d7"
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Drucom 0.1.0'
}


async def check_comment_total_async(session, uid):
    """
    Asynchronously check the total number of comments for a user ID.
    """
    params = {
        'full': 0,
        'limit': 1,
        'sort': 'cid',
        'direction': 'ASC',
        'author': uid
    }

    total = 0

    try:
        async with session.get(f"{BASE_URL}/comment.json", headers=HEADERS, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            last_page_url = data.get('last', '')
            if last_page_url:
                match = re.search(r'page=(\d+)', last_page_url)
                if match:
                    total = int(match.group(1))
    except Exception as e:
        pass

    return uid, total


def chunked_iterable(iterable, size):
    """
    Yield successive chunks of a given size from an iterable.
    """
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


async def transform_and_save_results(results, output_folder, page, file_semaphore):
    """
    Transform results into the desired format and save them to a JSON file.
    """
    transformed_data = {
        str(item[0]): {"total": item[1]} for item in results if item is not None
    }

    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"page_{page}.json")
    async with file_semaphore:  # Limit concurrent file writes
        async with aiofiles.open(output_file, 'w') as f:
            await f.write(json.dumps(transformed_data, separators=(',', ':')))


async def process_chunk_async(session, chunk):
    """ 
    Asynchronously process a chunk of UIDs and return results.
    """
    tasks = [check_comment_total_async(session, uid) for uid in chunk]
    return await asyncio.gather(*tasks, return_exceptions=False)


async def process_all_chunks_sequentially(uids, chunk_size, output_folder, start_page=1):
    """
    Process all UIDs in chunks sequentially with controlled concurrency.
    """
    connector = aiohttp.TCPConnector(limit=1000)  # Increase connection pool size
    file_semaphore = asyncio.Semaphore(50)  # Limit concurrent file writes to 50
    async with aiohttp.ClientSession(connector=connector) as session:
        chunks_total = sum(1 for _ in chunked_iterable(uids, chunk_size))
        for page, chunk in enumerate(chunked_iterable(uids, chunk_size), start=1):
            if page < start_page:
                continue  # Skip already processed pages
            start_time = time.time()
            results = await process_chunk_async(session, chunk)
            await transform_and_save_results(results, output_folder, page, file_semaphore)
            end_time = time.time()
            print(f"Processed chunk {page} / {chunks_total} in {end_time - start_time:.2f} seconds")


# Main processing.
uids = json.load(open('data/json/uids.json', 'r'))
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

chunk_size = 1000
start_page = int(sys.argv[1])  # Restart from page N

# Feature flag for testing.
TEST_MODE = False
if TEST_MODE:
    i_start = 0
    i_stop = 20000
    uids = uids[i_start:i_stop]

start_time = time.time()
asyncio.run(process_all_chunks_sequentially(uids, chunk_size, output_folder, start_page=start_page))
end_time = time.time()
print(f"Processed all chunks in {end_time - start_time:.2f} seconds")
