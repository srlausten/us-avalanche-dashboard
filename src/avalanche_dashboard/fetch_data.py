import requests
import io
import pandas as pd
import logging


def fetch_avy_data():
    # URL of the CAIC US Avalanche Data 1951-2022
    url = "https://avalanche.state.co.us/sites/default/files/2022-11/Accidents_2022_PUBLIC.xlsx"
    
    # Send an HTTP GET request to download the file
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Read the Excel file from the response content into a DataFrame
        with io.BytesIO(response.content) as stream:
            df = pd.read_excel(stream)
    
        # Now you can work with the DataFrame (e.g., df.head())
        logging.info("Avalanche Data loaded into DataFrame successfully.")

    return df
