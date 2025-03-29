import json
import os
import re
import requests
import pandas as pd

BASE_URL = "https://www.drupal.org/api-d7"

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Drucom 0.1.0'
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_comments_by_user(id: int) -> tuple:
    """
    Fetch comments by user.

    Returns
    -------
    tuple
        A tuple containing:
        - total: The count of comment for this user.
        - first: The first comment.
        - last: The last comment.
    """
    total = 0
    first_created = None
    last_created = None

    # Construct the URL for the API request
    PARAMS = {
        'author': id,
        'limit': 1,
        'sort': 'cid',
        'direction': 'ASC',
    }

    print(f"Fetching comments for user ID: {id}")
    response = requests.get(
        f"{BASE_URL}/comment.json", headers=HEADERS, params=PARAMS)

    data = response.json()
    last_page_url = data.get('last', '')

    # Use a regular expression to extract the number after "page="
    match = re.search(r'page=(\d+)', last_page_url)
    if match:
        total = int(match.group(1))
    else:
        total = 0

    if total <= 0:
        return None

    comments_list = data.get('list', [])
    first_created = comments_list[0].get('created', None)

    print(f"Fetching last comment for user ID: {id}")
    PARAMS['page'] = (total - 1)
    response = requests.get(
        f"{BASE_URL}/comment.json", headers=HEADERS, params=PARAMS)
    data = response.json()
    comments_list = data.get('list', [])
    last_created = comments_list[0].get('created', None)

    return (total, first_created, last_created)


# Print UIDs to one JSON file.
input_file = os.path.join(SCRIPT_DIR, '../data/json/uids.json')
if not os.path.exists(input_file):
    df = pd.read_parquet(os.path.join(SCRIPT_DIR, '../data/user.parquet'))
    uids = df['id'].unique()
    with open(os.path.join(SCRIPT_DIR, '../data/json/uids.json'), 'w') as f:
        json.dump(uids.tolist(), f)
else:
    with open(input_file, 'r') as f:
        uids = json.load(f)
        
# Print the number of unique UIDs
print(f"Fetching comments for {len(uids)} users...")

# For testing purposes, limit the number of UIDs to process.
uids = uids[:1000]

# For each UID, fetch the comments asycnchronously
comments = []
for uid in uids:
    result = fetch_comments_by_user(uid)
    if result is None:
        continue
    total, first_created, last_created = result
    comments.append({
        'uid': uid,
        'total': total,
        'first': first_created,
        'last': last_created
    })
    
# Convert the list of comments to a DataFrame
users = pd.DataFrame(comments)
# Drop rows with NaN values in the 'comments' column
users.dropna(subset=['comments'], inplace=True)

# Save the DataFrame to a Parquet file
output_file = os.path.join(SCRIPT_DIR, '../data/comments.parquet')
users.to_parquet(output_file, index=False)
print(f"Comments data saved to {output_file}")
# Print the first few rows of the DataFrame
print(users.head())
