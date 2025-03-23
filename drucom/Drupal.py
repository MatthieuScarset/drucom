# Extract data from Drupal.org API.
import requests


class Drupal:
    """
    Drupal.org API client.
    
    @example
    from drucom.Drupal import Drupal
    client = Drupal()
    client.get_organization({"title": "Drupal Association"})
    """

    def __init__(self):
        self.base_url = "https://www.drupal.org/api-d7"
        self.headers = {
            "User-Agent": "Drucom/1.0",
            "Accept": "application/json",
        }

    def get_data(self, resource, params={}):
        """
        Get data from Drupal.org API.
        @param string resource: API resource such as 'node.json'.
        @param dict params: Query parameters
        @return dict: JSON response from API.
        """
        url = f"{self.base_url}/{resource}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                raise requests.exceptions.RequestException(
                    f"HTTP status code: {response.status_code}"
                )
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
        return None

    def get_organization(self, params={}):
        """
        Get organization data from Drupal.org API.
        @code
        params = {"title": "Drupal Association"}
        data = Drupal.get_organization(params)
        print(data)        
        @endcode
        """
        if 'type' not in params:
            params['type'] = 'organization'
        return self.get_data("node.json", params)

    def get_user(self, params={}):
        """
        Get user data from Drupal.org API.
        @code
        params = {
            "name": "Dries",
            "field_da_ind_membership": "Current"
        }
        data = Drupal.get_user(params)
        print(data)        
        @endcode
        """
        return self.get_data("user.json", params)

    def get_comments(self, params={}):
        """
        Get user data from Drupal.org API.
        @code
        params = {"author": "1",}
        data = Drupal.get_comments(params)
        print(data)        
        @endcode
        """
        return self.get_data("comments.json", params)
