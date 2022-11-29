import requests


class SpringerClient(object):
    BASE_URL = "https://api.springernature.com/bookmeta/v1/json"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_book_data(self, api_response):
        book_api_data = api_response["records"][0]
        book_data = {
            "language": book_api_data["language"],
            "description": book_api_data["abstract"],
            "publication_date": book_api_data["publicationDate"],
        }
        return book_data

    def get_book_from_api(self, doi):
        """docstring for get_book_data"""
        # check if "doi:" is in beginning of string; if not, add
        doi = f"doi:{doi}" if not doi.startswith("doi") else doi
        try:
            params = {"q": doi, "api_key": self.api_key}
            response = requests.get(self.api_endpoint, params=params)
            response.raise_for_status()
            page_data = response.json()
            return page_data
        except Exception as err:
            raise Exception(err)

    def parse_subjects_from_json(self):
        """docstring for get_subjects"""

    pass
