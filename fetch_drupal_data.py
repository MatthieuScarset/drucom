import os
import jq
import json
from argparse import ArgumentParser
import requests

BASE_URL = "https://www.drupal.org/api-d7"

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Drucom 0.1.0"
}


def get_mapping(name):
    """Get the mapping for a specific dataset."""

    # Define mappings for each type
    user_mapping = {
        "id": ".uid",
        "title": ".name",
        "fname": "(.field_first_name // null)",
        "lname": "(.field_last_name // null)",
        "created": ".created",
        "da_membership": "(.field_da_ind_membership // null)",
        "slack": "(.field_slack // null)",
        "mentors": "(if (.field_mentors | type == 'array') then .field_mentors | map(.id | tostring) else [] end)",
        "countries": "(.field_country // null)",
        "language": "(.field_user_primary_language // null)",
        "languages": "(.field_languages // [])",
        "timezone": "(.timezone // null)",
        "region": "(if .timezone | length > 0 then (.timezone | tostring | split('/') | first) else null end)",
        "city": "(if .timezone | length > 0 then (.timezone | tostring | split('/') | last) else null end)",
        "organizations": "(if (.field_organizations | type == 'array') then .field_organizations | map(.id | tostring) else [] end)",
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
        "url": "(if (.field_link | type == 'object') then .field_link.url else null end)",
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
        "maintenance_status": "(if (.taxonomy_vocabulary_44 | type == 'object') then .taxonomy_vocabulary_44.id else null end)",
        "development_status": "(if (.taxonomy_vocabulary_46 | type == 'object') then .taxonomy_vocabulary_46.id else null end)",
        "categories": "(if (.taxonomy_vocabulary_3 | type == 'array') then .taxonomy_vocabulary_3 | map(.id | tostring) else [] end)"
    }

    event_mapping = {
        "id": ".nid",
        "title": ".title",
        "from": "(.field_date_of_event.value // null)",
        "to": "(.field_date_of_event.value2 // null)",
        "duration": "(.field_date_of_event.duration // null)",
        "event_type": "(.field_event_type // [] | join(''))",
        "event_format": "(.field_event_format // [] | join(''))",
        "author": "(.author.id // null)",
        "speakers": "(if (.field_event_speakers | type == 'array') then .field_event_speakers | map(.id | tostring) else [] end)",
        "sponsors": "(if (.field_event_sponsors | type == 'array') then .field_event_sponsors | map(.id | tostring) else [] end)",
        "volunteers": "(if (.field_event_volunteers | type == 'array') then .field_event_volunteers | map(.id | tostring) else [] end)",
        "organizers": "(if (.field_organizers | type == 'array') then .field_organizers | map(.id | tostring) else [] end)",
        "city": "(if (.field_event_address | type == 'object') then .field_event_address.locality else null end)",
        "country": "(if (.field_event_address | type == 'object') then .field_event_address.country else null end)"
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
        "taxonomy_terms": taxonomy_terms_mapping,
        "theme": theme_mapping
    }
    return mappings.get(name, None)


def get_total_pages(url, params):
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
        # Request full 0 to get the last page.
        data = requests.get(url, headers=HEADERS, params={
                            **params, 'full': 0}).json()
        return int(data['last'].split('page=')[1])
    except Exception as e:
        print(f"Error fetching total pages: {e}")
        return 0


def fetch_pages(output_folder, total_pages, url, params, mapping):
    """
    Fetch data from the Drupal API and save it to a file.
    Args:
        output_folder (str): The folder to save the data.
        url (str): The URL to request.
        params (dict): The parameters to include in the request.
        page (int): The page number to fetch.
    """
    for page in range(total_pages):
        print(f"Fetching page {page} of {total_pages}")
        params['page'] = page
        data = requests.get(url, headers=HEADERS,
                            params=params, stream=True).json()
        with open(os.path.join(output_folder, f"page_{page}.json"), 'w') as f:
            # Process the data here based on mapping
            jq_filter = jq.compile(mapping)
            data['list'] = jq_filter.transform(data['list'])
            # Save the transformed data to a file
            f.write(json.dumps(data['list'], indent=4))

def process(output_folder, url, params, mapping):
    """
    Process the data from the Drupal API and save it to a file.
    """
    total_pages = get_total_pages(url, params)
    if total_pages > 0:
        fetch_pages(output_folder, total_pages, url, params, mapping)
    return total_pages
    

def main():
    """
    Main function to fetch data from Drupal API.
    """
    parser = ArgumentParser(description="Fetch data from Drupal API")
    parser.add_argument(
        '--name', type=str, default="", help="Name of the dataset to retrieve from d.o")
    args = parser.parse_args()
    dataset_name = args.name
    if not len(dataset_name):
        print('missing argument --name')
        return

    # Get the mapping for the dataset
    mapping = get_mapping(dataset_name)
    if mapping is None:
        print(f"Unknown dataset: {dataset_name}")
        return

    # Make output_folder relative to the script directory
    output_folder = os.path.join(os.path.dirname(
        __file__), f"../data/json/{dataset_name}")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Events.
    if dataset_name == 'event':
        endpoint = 'node.json'
        params = {'type': 'event', 'sort': 'nid', 'direction': 'ASC'}
        
    # user
    if dataset_name == 'user':
        endpoint = 'user.json'
        params = {'sort': 'uid', 'direction': "ASC"}

    if dataset_name == "organization":
        endpoint: 'node.json'
        params = {'type': 'organization', 'sort': 'nid', 'direction': 'ASC'}
        
    # module
    # fetch_data "module" "node.json" "type=project_module&sort=nid&direction=ASC" "$module_mapping"
    # module_terms
    # fetch_data "module_terms" "taxonomy_term.json" "vocabulary[]=3&vocabulary[]=44&vocabulary[]=46&sort=tid&direction=ASC" "$taxonomy_terms_mapping"
    # theme
    # fetch_data "theme" "node.json" "type=project_theme&sort=nid&direction=ASC" "$theme_mapping"
    # echo "Usage: $0 {user|organization|event|module|module_terms}"
    
    url = f"{BASE_URL}/{endpoint}"
    total_pages = process(output_folder, url, params, mapping)
    print(f"Processed {total_pages} pages of data for {dataset_name}")
    return

if __name__ == "__main__":
    main()
