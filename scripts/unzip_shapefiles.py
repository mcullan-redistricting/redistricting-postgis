import os
import re

from glob import glob
from zipfile import ZipFile

data_path = os.environ.get('DATA_PATH', '../data')

def unzip_shapefiles(*args, **kwargs):
    """Extract zipfile(s) in respective parent directory given filepath(s)"""
    
    def unzip_shapefile(path_to_zip, **kwargs):
        def fn():
            regex = re.compile(r'(.*)\/(.*\.zip)')
            directory, filename = regex.match(path_to_zip).groups()

            with ZipFile(path_to_zip, 'r') as file:
                if kwargs.get('debug'):
                    print(f'  extracting {path_to_zip}')
                if not kwargs.get('print_only'):
                    file.extractall(directory)

            if kwargs.get('delete_zip'):
                if kwargs.get('debug'):
                    print(f'  removing {path_to_zip}')
                if not kwargs.get('print_only'):
                    os.remove(path_to_zip)
            else:
                print('')
        
        return fn
            
    for arg in args:
        if os.path.exists(arg):
            if kwargs.get('debug'):
                    print(f'unzip_shapefile{arg}, {kwargs})')
            unzip_shapefile(arg, **kwargs)()
            print('')

    
    return

if __name__ == '__main__':


    print(data_path)
    zips = glob(f'{data_path}/precincts-elections/**/*.zip')
    unzip_shapefiles(*zips, debug=True, delete_zip=True, print_only=False)