import json
import requests
from tqdm import tqdm

BASE_URL = "https://www.drupal.org/api-d7/user.json"
HEADERS = {
    "User-Agent": "Drucom/1.0",
    "Accept": "application/json",
}


def get_data(params: dict = None):
    return requests.get(BASE_URL, headers=HEADERS, params=params).json()


def save_data(file_path, params: dict = None):
    try:
        data = get_data(params)
        with open(file_path, "w") as f:
            f.write(json.dumps(data['list'], indent=2, sort_keys=True))
    except Exception as e:
        print(f'Error during extract_data(): {str(e)}')
    return True


def main():
    start = 0
    end = get_data()['last'].split('=')[1]
    print(f"Retrieving user data from page {start} to {end}")
    for i in tqdm(range(start, int(end) + 1)):
        save_data(f"data/users.{i}.json", {'page': i})

if __name__ == '__main__':
    main()
