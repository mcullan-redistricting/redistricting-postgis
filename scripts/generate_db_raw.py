import os
import re

import geoalchemy2
import geopandas as gpd
from glob import glob
import pandas as pd
import psycopg2
import sqlalchemy


data_path = os.path.abspath('../data')
shape_path = f'{data_path}/precincts-elections'

user = os.environ.get('POSTGRES_USER', None)
password = os.environ.get('POSTGRES_PASSWORD', None)
db_name = os.environ.get('DB_NAME', None)


def parse_metadata(path_to_readme):
    
    data_dict = {}
    
    with open(path_to_readme, 'r') as file:
        readme = file.read()
        
    regex_metadata = re.compile(
    r'`(?P<column>.*?)`: (?P<description>.*?)\n')

    fields = regex_metadata.finditer(readme)
    
    for field in fields:
        column = field['column']
        description = field['description']

        data_dict[column] = description
        
    return data_dict

def parse_all_metadata(shape_path):
    
    out = {}
    regex = re.compile(r'(\w\w)-shapefiles')
    all_readme_paths= glob(f'{shape_path}/**/README*')

    all_readme = {}
    for path in all_readme_paths:
        abbreviation = regex.search(path).groups()[0].lower()
        all_readme[abbreviation] = path
        
    for abbr, path in all_readme.items():
        out[abbr] = parse_metadata(path)
    
    return out

def make_metadata_frame(state, metadata):
    items = metadata.items()
    df_metadata = pd.DataFrame(items, 
                               columns=['column_name' ,'description']
                              )
    df_metadata['description'] = df_metadata['description'].str.lower()
    df_metadata['state'] = state
    df_metadata = df_metadata.set_index(['state', 'column_name'])
    return df_metadata
    
def make_full_metadata_df(shape_path):
    all_metadata = parse_all_metadata(shape_path)

    all_metadata_dfs = {
    state:make_metadata_frame(state, metadata)
    for state, metadata in all_metadata.items()}

    metadata_df = pd.concat(all_metadata_dfs.values())

    return metadata_df

def remove_duplicate_columns(df, ignore_cols='geometry'):
    identical_columns = {}
    for col1 in df.drop(ignore_cols, 1):
        for col2 in df.drop([col1, ignore_cols], 1):
            if df[col1].equals(df[col2]):
                col1, col2 = sorted([col1, col2])
                identical_columns[col1]=col2

    identical_columns

    df = df.drop(identical_columns.values(), 1)
    
    return df

def make_full_shp_df(shape_path):
        all_shp_paths= glob(f'{shape_path}/**/*.shp')

        all_shp = {}
        regex = re.compile(r'(\w\w)-shapefiles')
        for path in all_shp_paths:
            abbreviation = regex.search(path).groups()[0].lower()
            all_shp[abbreviation] = path  

        all_shp_df = {state: gpd.read_file(shp) for state, shp in all_shp.items()}
        
        return all_shp_df

def geo_df_to_sql(df,name, engine):
    # Convert `'geom'` column in GeoDataFrame `gdf` to hex
        # Note that following this step, the GeoDataFrame is just a regular DataFrame
        # because it does not have a geometry column anymore. Also note that
        # it is assumed the `'geom'` column is correctly datatyped.
    
    def wkb_hexer(line):
        return line.wkb_hex

    df.columns = df.columns.str.lower()
    
    if 'geometry' in df.columns:  
        
        print(f'Writing {name} to database.')
        
        df['geom'] = df['geometry'].apply(wkb_hexer)
        df = df.drop('geometry', 1)
        df.to_sql(
            name,
            engine,
            if_exists='replace',
            method='multi'
        )
    else:
        print(f'No geometry column found for {name}')

if __name__ == '__main__':


    engine = sqlalchemy.create_engine(
        f'postgresql://{user}:{password}@localhost/{db_name}'
    )

    metadata_df = make_full_metadata_df(shape_path)
    metadata_df.to_sql(
        'metadata',
        engine,
        if_exists='replace',
        index=True,
        index_label = ['state', 'column_name'],
        dtype=sqlalchemy.String,
        method='multi'
    )

    all_shp_df = make_full_shp_df(shape_path)
    for state, df in all_shp_df.items():
        geo_df_to_sql(df, state, engine)


    




