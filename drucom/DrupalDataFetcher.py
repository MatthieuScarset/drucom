import os
import json
import asyncio
import aiohttp
import requests
from aiofiles import open as aio_open
import jq


class DrupalDataFetcher:
    """
    A class to fetch data from the Drupal.org API and save it in JSON format.

    It can fetch users, organizations, modules, events and themes from d.o.
    It uses asynchronous requests to improve performance.
    It transforms raw data using jq filters to extract and format relevant field.
    It saves the data in JSON files in the `../data/json` directory. 
    """

    BASE_URL = "https://www.drupal.org/api-d7"

    HEADERS = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Drucom 0.1.0"
    }

    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.mapping = self.get_mapping(dataset_name)
        if self.mapping is None:
            raise ValueError(f"Unknown dataset: {dataset_name}")
        self.output_folder = os.path.join(
            os.path.dirname(__file__), f"../data/json/{dataset_name}"
        )
        os.makedirs(self.output_folder, exist_ok=True)

    @staticmethod
    def get_mapping(name):
        """
        Get the mapping for a specific dataset.
        The mapping is used to transform the data from the Drupal API into a desired format.
        The values in the mapping are jq filters that specify how to extract and transform the data.
        Args:
            name (str): The name of the dataset.
        Returns:
            dict: The mapping for the dataset.
        """
        user_mapping = {
            "id": ".uid",
            "title": ".name",
            "fname": "(.field_first_name // null)",
            "lname": "(.field_last_name // null)",
            "created": ".created",
            "da_membership": "(.field_da_ind_membership // null)",
            "slack": "(.field_slack // null)",
            "mentors": "(if (.field_mentors | type == \"array\") then .field_mentors | map(.id | tostring) else [] end)",
            "countries": "(.field_country // null)",
            "language": "(.field_user_primary_language // null)",
            "languages": "(.field_languages // [])",
            "timezone": "(.timezone // null)",
            "region": "(if .timezone | length > 0 then (.timezone | tostring | split(\"/\") | first) else null end)",
            "city": "(if .timezone | length > 0 then (.timezone | tostring | split(\"/\") | last) else null end)",
            "organizations": "(if (.field_organizations | type == \"array\") then .field_organizations | map(.id | tostring) else [] end)",
            "industries": "(.field_industries // null)",
            "contributions": "(.field_contributed // null)",
            "events": "(.field_events_attended // null)"
        }

        organization_mapping = {
            "id": ".nid",
            "title": ".title",
            "created": ".created",
            "changed": ".changed",
            "author": "(.author.id // null)",
            "url": "(if (.field_link | type == \"object\") then .field_link.url else null end)",
            "budget": "(.field_budget // null)",
            "headquarters": "(.field_organization_headquarters // null)"
        }

        module_mapping = {
            "id": ".nid",
            "title": ".title",
            "created": ".created",
            "changed": ".changed",
            "author": "(.author.id // null)",
            "slug": ".field_project_machine_name",
            "stars": "(.flag_project_star_user // [] | length // 0)",
            "security_status": ".field_security_advisory_coverage",
            "maintenance_status": "(if (.taxonomy_vocabulary_44 | type == \"object\") then .taxonomy_vocabulary_44.id else null end)",
            "development_status": "(if (.taxonomy_vocabulary_46 | type == \"object\") then .taxonomy_vocabulary_46.id else null end)",
            "categories": "(if (.taxonomy_vocabulary_3 | type == \"array\") then .taxonomy_vocabulary_3 | map(.id | tostring) else [] end)"
        }

        event_mapping = {
            "id": ".nid",
            "title": ".title",
            "from": "(.field_date_of_event.value // null)",
            "to": "(.field_date_of_event.value2 // null)",
            "duration": "(.field_date_of_event.duration // null)",
            "event_type": "(.field_event_type // [] | join(\"\"))",
            "event_format": "(.field_event_format // [] | join(\"\"))",
            "author": "(.author.id // null)",
            "speakers": "(if (.field_event_speakers | type == \"array\") then .field_event_speakers | map(.id | tostring) else [] end)",
            "sponsors": "(if (.field_event_sponsors | type == \"array\") then .field_event_sponsors | map(.id | tostring) else [] end)",
            "volunteers": "(if (.field_event_volunteers | type == \"array\") then .field_event_volunteers | map(.id | tostring) else [] end)",
            "organizers": "(if (.field_organizers | type == \"array\") then .field_organizers | map(.id | tostring) else [] end)",
            "city": "(if (.field_event_address | type == \"object\") then .field_event_address.locality else null end)",
            "country": "(if (.field_event_address | type == \"object\") then .field_event_address.country else null end)"
        }

        taxonomy_terms_mapping = {
            "id": ".tid",
            "name": ".name"
        }

        theme_mapping = {
            "id": ".nid",
            "title": ".title",
            "created": ".created",
            "changed": ".changed",
            "author": "(.author.id // null)",
            "slug": ".field_project_machine_name",
            "stars": "(.flag_project_star_user // [] | length // 0)"
        }

        mappings = {
            "user": user_mapping,
            "organization": organization_mapping,
            "module": module_mapping,
            "event": event_mapping,
            "module_terms": taxonomy_terms_mapping,
            "theme": theme_mapping
        }

        return mappings.get(name, None)

    def get_total_pages(self, url, params):
        """
        Get the total number of pages for a given URL and parameters.
        This function makes a request to the Drupal API and extracts the total number of pages
        from the last page URL.
        Args:
            url (str): The URL to request.
            params (dict): The parameters to include in the request.
        Returns:
            int: The total number of pages.
        """
        try:
            data = requests.get(url, headers=self.HEADERS, params={
                                **params, 'full': 0, 'limit': 1}).json()
            total_pages = int(data['last'].split('page=')[1])
            if total_pages == 0:
                return 0

            data = requests.get(url, headers=self.HEADERS, params={
                                **params, 'full': 0}).json()
            return int(data['last'].split('page=')[1])
        except Exception as e:
            print(f"Error fetching total pages: {e}")
            return 0

    async def fetch_page(self, session, url, params, page):
        """
        Fetch a single page asynchronously and save the transformed data.
        Args:
            session (aiohttp.ClientSession): The session to use for the request.
            url (str): The URL to request.
            params (dict): The parameters to include in the request.
            page (int): The page number to fetch.
        """
        params['page'] = page
        try:
            async with session.get(url, params=params) as response:
                data = await response.json()
                jq_filter_string = '{' + ', '.join(
                    [f'"{key}": {value}' for key, value in self.mapping.items()]) + '}'
                jq_filter = jq.compile(jq_filter_string)
                transformed_data = [jq_filter.transform(
                    item) for item in data.get('list', [])]

                output_file = os.path.join(
                    self.output_folder, f"page_{page}.json")
                async with aio_open(output_file, 'w') as f:
                    await f.write(json.dumps(transformed_data, separators=(',', ':')))
                print(f"Saved page {page + 1} to {output_file}")
        except Exception as e:
            print(f"Error fetching page {page}: {e}")

    async def fetch_all_pages(self, url, params, total_pages, max_concurrent_requests=100):
        """
        Fetch all pages asynchronously with a limit on concurrent requests.
        Args:
            url (str): The URL to request.
            params (dict): The parameters to include in the request.
            total_pages (int): The total number of pages to fetch.
            max_concurrent_requests (int): The maximum number of concurrent requests.
        """
        connector = aiohttp.TCPConnector(limit=max_concurrent_requests)
        async with aiohttp.ClientSession(headers=self.HEADERS, connector=connector) as session:
            tasks = [
                self.fetch_page(session, url, params, page)
                for page in range(total_pages)
            ]
            await asyncio.gather(*tasks)

    def process(self, url, params):
        """
        Process the data asynchronously.
        Args:
            url (str): The URL to request.
            params (dict): The parameters to include in the request.
        Returns:
            int: The total number of pages processed.
        """
        total_pages = self.get_total_pages(url, params)
        if total_pages >= 0:
            asyncio.run(self.fetch_all_pages(url, params, total_pages))
        return total_pages

    def run(self):
        """
        Run the data fetching process.
        This function determines the endpoint and parameters based on the dataset name,
        and then calls the process method to fetch the data.
        Raises:
            ValueError: If the dataset name is unknown.
        """
        if self.dataset_name == 'event':
            endpoint = 'node.json'
            params = {'type': 'event', 'sort': 'nid', 'direction': 'ASC'}
        elif self.dataset_name == 'user':
            endpoint = 'user.json'
            params = {'sort': 'uid', 'direction': "ASC"}
        elif self.dataset_name == 'organization':
            endpoint = 'node.json'
            params = {'type': 'organization',
                      'sort': 'nid', 'direction': 'ASC'}
        elif self.dataset_name == 'module':
            endpoint = 'node.json'
            params = {'type': 'project_module',
                      'sort': 'nid', 'direction': 'ASC'}
        elif self.dataset_name == 'module_terms':
            endpoint = 'taxonomy_term.json'
            params = {'vocabulary[]': ['3', '44', '46'],
                      'sort': 'tid', 'direction': 'ASC'}
        elif self.dataset_name == 'theme':
            endpoint = 'node.json'
            params = {'type': 'project_theme',
                      'sort': 'nid', 'direction': 'ASC'}
        else:
            raise ValueError(f"Unknown dataset: {self.dataset_name}")

        url = f"{self.BASE_URL}/{endpoint}"
        total_pages = self.process(url, params)
        print(
            f"Processed {total_pages + 1} pages of data for {self.dataset_name}")

    def main(dataset_name: str):
        """
        Main function to fetch data from Drupal API.
        Requires the dataset name as an argument.    
        """
        try:
            fetcher = DrupalDataFetcher(dataset_name)
            fetcher.run()
        except ValueError as e:
            print(e)
