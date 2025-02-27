import time
import requests
import os
import json

from config.config import URL_BASE

class GraphAPIClient:
    """
    A client for interacting with the Graph API, providing functionality to fetch data
    and save it to a specified location, including support for pagination and retry on rate limits.
    """

    def __init__(self, max_retries=5, initial_wait=240):
        self.max_retries = max_retries
        self.initial_wait = initial_wait  # Initial wait time in seconds

    def fetch_data(self, endpoint, params, output_dir, file_name, extend_data=True, page=True):
        """
        Fetch data from the Graph API for a given endpoint and parameters, handling pagination and rate limits.

        Args:
            endpoint (str): API endpoint to query.
            params (dict): Query parameters to include in the request.
            output_dir (str): Directory where the output file will be saved.
            file_name (str): Name of the file to save the fetched data.
            extend_data (bool): Whether to extend the data when paginating.
            page (bool): Whether the request is for a Facebook Page (True) or an Ad Account (False).

        Raises:
            Exception: If the API response status is not 200 after retries.
        """
        url = f"{URL_BASE}{endpoint}"
        params["access_token"] = os.getenv("ACCESS_TOKEN",'')

        if not params["access_token"]:
            raise EnvironmentError("Access token is not set.")

        all_data = []
        attempt = 0  # Track retry attempts

        while url:
            try:
                response = requests.get(url, params=params, timeout=200)

                if response.status_code == 200:
                    data = response.json()
                    if extend_data:
                        all_data.extend(data.get("data", []))
                        paging = data.get("paging", {})
                        url = paging.get("next", None)  # Get next page URL
                        params = {}  # Reset params
                    else:
                        all_data = data
                        url = None

                elif response.status_code == 400:
                    error_data = response.json()
                    error_code = error_data.get("error", {}).get("code", 0)
                    error_subcode = error_data.get("error", {}).get("error_subcode", 0)

                    # **Handle Rate Limit Error**
                    if error_code == 17 or error_subcode == 2446079:
                        attempt += 1
                        if attempt >= self.max_retries:
                            raise requests.exceptions.RequestException(
                                f"Rate limit reached. Max retries ({self.max_retries}) exceeded."
                            )

                        wait_time = self.initial_wait * (2 ** (attempt - 1))
                        print(f"Rate limit reached. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)  # Wait and retry
                        continue  # Restart loop

                    else:
                        raise requests.exceptions.RequestException(
                            f"Error fetching data: {response.status_code}, {response.text}"
                        )

                else:
                    raise requests.exceptions.RequestException(
                        f"Error fetching data: {response.status_code}, {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                print(f"API request failed: {str(e)}")
                raise requests.exceptions.RequestException(
                        f"Error fetching data: {response.status_code}, {response.text}"
                    )

        # Save all the fetched data to the file
        self.__write_to_file(output_dir, file_name, {"data": all_data})

    def __write_to_file(self, output_dir, file_name, data):
        """
        Save data to a JSON file in the specified output directory.
        
        Args:
            output_dir (str): Directory where the file will be saved.
            file_name (str): Name of the output file.
            data (dict): Data to save.
        """
        # Check if "data" exists and is empty
        if isinstance(data, dict) and "data" in data and not data["data"]:
            print(f"⚠️ No data found. Skipping file creation for {file_name}")
            return  # Exit the function without writing

        os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print(f"✅ Data successfully saved to {file_path}")
