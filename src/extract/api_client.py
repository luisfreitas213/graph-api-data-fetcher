import requests
import os
import json

from config.config import URL_BASE

class GraphAPIClient:
    """
    A client for interacting with the Graph API, providing functionality to fetch data
    and save it to a specified location.
    """

    def __init__(self):
        pass

    def fetch_data(self, endpoint, params, output_dir, file_name):
        """
        Fetch data from the Graph API for a given endpoint and parameters.

        Args:
            endpoint (str): API endpoint to query.
            params (dict): Query parameters to include in the request.
            output_dir (str): Directory where the output file will be saved.
            file_name (str): Name of the file to save the fetched data.

        Raises:
            Exception: If the API response status is not 200.
        """
        url = f"{URL_BASE}{endpoint}"
        params["access_token"] = os.getenv("PAGE_ACCESS_TOKEN")

        # Validate access token
        if not params["access_token"]:
            raise EnvironmentError("PAGE_ACCESS_TOKEN environment variable is not set.")

        response = requests.get(url, params=params, timeout=200)

        if response.status_code == 200:
            data = response.json()
            self.__write_to_file(output_dir, file_name, data)
        else:
            raise requests.exceptions.RequestException(
                f"Error fetching data: {response.status_code}, {response.text}")

    def __write_to_file(self, output_dir, file_name, data):
        """
        Save data to a JSON file in the specified output directory.

        Args:
            output_dir (str): Directory where the file will be saved.
            file_name (str): Name of the output file.
            data (dict): Data to save.
        """
        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print(f"Data successfully saved to {file_path}")
