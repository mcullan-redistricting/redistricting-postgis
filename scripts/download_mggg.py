from io import BytesIO

from bs4 import BeautifulSoup
import requests
import os
import pandas as pd
from constants import STATES
from zipfile import ZipFile


data_path = os.environ.get('DATA_PATH', '../data')

def download_mggg_state_zip(state_abbreviation, filepath, overwrite = False):
    url = f'https://github.com/mggg-states/{state_abbreviation}-shapefiles/archive/master.zip'

    response = requests.get(url)

    if response.ok:
        full_path = filepath + f'/precincts-elections/'

        if not os.path.exists(full_path):
            os.mkdir(full_path)

        zip_name = f'{state_abbreviation}-shapefiles-master.zip'

        full_filepath = f'{full_path}/{zip_name}'

        if overwrite or not os.path.exists(full_filepath):
            with open(full_filepath, 'wb') as file:
                file.write(response.content)

            print(f'Extracting {state_abbreviation} zip file.')


            with ZipFile(full_filepath) as file:
                file.extractall(full_path)

            os.remove(full_filepath)

    if response.status_code == 404:
        print(f'404 returned for {state_abbreviation}.')
    
    return
def get_mggg_states_metadata(state_abbreviation):
    url = f'https://github.com/mggg-states/{state_abbreviation}-shapefiles/blob/master/README.md'

    response = requests.get(url)

    if response.ok:
        print(f'Downloaded {state_abbreviation} metadata.')
        soup = BeautifulSoup(response.text, 'lxml')

        metadata = soup.select('li:has(code)')
        data_dict = {}

        for line in metadata:
            k,v = line.text.split(': ')
            data_dict[k] = v

        return data_dict
    if response.status_code == 404:
        print('Could not complete request due to 404 error.')
        
        
def download_mggg_shapefile(state_abbreviation, filepath):
    url = f'https://github.com/mggg-states/{state_abbreviation}-shapefiles/raw/master/{state_abbreviation}_VTD.zip'
    response = requests.get(url)

    if response.ok:
        print(f'Downloaded {state_abbreviation} zip file.')
        full_path = filepath + f'/{state_abbreviation}_VTD'
        zip_name = f'{state_abbreviation}_VTD.zip'

        with open(f'{full_path}/{zip_name}', 'wb') as file:
            file.write(response.content)

        with ZipFile(f'{full_path}/{zip_name}') as file:
            file.extractall(filepath + '/NC_VTD')

        os.remove(f'{full_path}/{zip_name}')

    if response.status_code == 404:
        print(f'404 returned for {state_abbreviation}.')
    
    return
    
def download_mggg_state(state_abbreviation, filepath):
    
    # If directory doesn't exist, create it
    full_path = filepath + f'/precincts-elections/{state_abbreviation}_VTD'
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    
    # Download metadata and save to constants.py
    data_dict = get_mggg_states_metadata(state_abbreviation)

    with open(f'{full_path}/metadata.py', 'w') as file:
        file.write(f'DATA_DICT = {data_dict}')
    
    # Download shapefile and election data
    download_mggg_shapefile(state_abbreviation, filepath)
    
if __name__ == '__main__':

    state_abbvreviations = STATES.values()

    for abbreviation in list(state_abbvreviations):
        download_mggg_state_zip(abbreviation, data_path)