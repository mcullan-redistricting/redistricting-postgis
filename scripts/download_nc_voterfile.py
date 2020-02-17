"""
Downloads North Carolina voterfile and voter history, then extracts to data path.
"""
from io import BytesIO
from bs4 import BeautifulSoup

import os
import requests
import pandas as pd
from zipfile import ZipFile

from download_mggg import download_mggg_state

data_path = os.environ.get('DATA_PATH', '../data')


def download_zip(zip_url, filepath):
    print('Making request ...........')
    response = requests.get(zip_url)
    zip_content = BytesIO(response.content)

    with ZipFile(zip_content) as file:
        print(f'Extracting file to {filepath}.....')
        file.extractall(filepath)
        
    return 


def download_nc_voterfile_voterhistory(filepath):
	ncvoter_statewide_url = \
	'https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvoter_Statewide.zip'

	ncvhis_statewide_url = \
	'https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvhis_Statewide.zip'


	download_zip(ncvoter_statewide_url, filepath)
	download_zip(ncvhis_statewide_url, filepath)


def download_nc_precincts_elections(filepath):
	"""Downloads Voter Tabulation District shapefiles and election data from github.com/mggg-states."""

	nc_shapefile_url = 'https://github.com/mggg-states/NC-shapefiles/blob/master/NC_VTD.zip'
	nc_shapefile_metadata_url = 'https://github.com/mggg-states/NC-shapefiles/blob/master/NC_VTD.zip'

	download_zip(nc_shapefile_url, filepath)


if __name__ == '__main__':

	download_nc_voterfile_voterhistory(f'{data_path}/voter-file')
