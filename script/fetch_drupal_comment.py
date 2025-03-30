import asyncio
import aiohttp
import json
import os
import re
import pandas as pd

BASE_URL = "https://www.drupal.org/api-d7"
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Drucom 0.1.0'
}
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


async def fetch_comments_by_user_async(session, uid, semaphore):
    """
    Fetch comments for a user asynchronously with a semaphore.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp session to use for the request.
    uid : int
        The user ID.
    semaphore : asyncio.Semaphore
        Semaphore to limit the number of concurrent requests.

    Returns
    -------
    dict
        A dictionary containing the user's UID, total comments, first comment timestamp, and last comment timestamp.
    """
    async with semaphore:  # Limit the number of concurrent requests
        try:
            params = {
                'author': uid,
                'limit': 1,
                'sort': 'cid',
                'direction': 'ASC',
            }

            async with session.get(f"{BASE_URL}/comment.json", headers=HEADERS, params=params) as response:
                data = await response.json()
                last_page_url = data.get('last', '')
                comments_list = data.get('list', [])

                # Extract total pages
                total = 0
                if last_page_url:
                    match = re.search(r'page=(\d+)', last_page_url)
                    if match:
                        total = int(match.group(1))

                # Extract first comment timestamp
                first_created = comments_list[0].get('created', None) if comments_list else None

                # Fetch last comment if total pages > 1
                last_created = None
                if total > 1:
                    params['page'] = total - 1
                    async with session.get(f"{BASE_URL}/comment.json", headers=HEADERS, params=params) as last_response:
                        last_data = await last_response.json()
                        last_comments_list = last_data.get('list', [])
                        last_created = last_comments_list[0].get('created', None) if last_comments_list else None

                return {
                    'uid': uid,
                    'total': total,
                    'first': first_created,
                    'last': last_created
                }
        except Exception as e:
            print(f"Error fetching comments for user {uid}: {e}", flush=True)
            return None


async def fetch_all_comments(uids, batch_size=10000):
    """
    Fetch comments for all users asynchronously in batches.

    Parameters
    ----------
    uids : list
        List of user IDs.
    batch_size : int
        Number of UIDs to process in each batch.

    Returns
    -------
    list
        A list of dictionaries containing comments data for each user.
    """
    semaphore = asyncio.Semaphore(1000)  # Limit to 1000 concurrent requests
    all_results = []

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(uids), batch_size):
            batch = uids[i:i + batch_size]
            print(f"Processing batch {i // batch_size + 1} with {len(batch)} users...", flush=True)
            tasks = [fetch_comments_by_user_async(session, uid, semaphore) for uid in batch]
            results = await asyncio.gather(*tasks)
            all_results.extend(results)

    return all_results


def main():
    # Load UIDs
    input_file = os.path.join(SCRIPT_DIR, '../data/json/uids.json')
    if not os.path.exists(input_file):
        df = pd.read_parquet(os.path.join(SCRIPT_DIR, '../data/user.parquet'))
        uids = df['id'].unique()
        with open(input_file, 'w') as f:
            json.dump(uids.tolist(), f)
    else:
        with open(input_file, 'r') as f:
            uids = json.load(f)

    # Limit the number of UIDs for testing
    #uids = uids[:20000]

    print(f"Fetching comments for {len(uids)} users asynchronously...", flush=True)

    # Fetch comments asynchronously in batches
    comments = asyncio.run(fetch_all_comments(uids))

    # Convert to DataFrame
    users = pd.DataFrame(comments)

    # Drop rows with total = 0
    users = users[users['total'] > 0]

    # Save to Parquet
    output_file = os.path.join(SCRIPT_DIR, '../data/comments.parquet')
    users.to_parquet(output_file, index=False)
    print(f"Comments data saved to {output_file}", flush=True)
    print(users.head(), flush=True)


if __name__ == "__main__":
    main()
