import requests
import zipfile
import os

def download_file(url, output_file):
    """
    Downloads a file from the given URL and saves it to the specified output path.

    Parameters:
        url (str): The URL of the file to download.
        output_file (str): The path where the downloaded file will be saved.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an HTTPError for bad responses
    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)

def unzip_file(zip_file, destination_folder):
    """
    Extracts a zip file to the specified destination folder.

    Parameters:
        zip_file (str): The path to the zip file.
        destination_folder (str): The folder where the contents will be extracted.
    """
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)  # Create the folder if it doesn't exist
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)