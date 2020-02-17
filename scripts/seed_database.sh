#!/bin/bash


read -p 'Enter postgres username: ' username

read -sp 'Enter postgres password: ' password

echo 

read -p 'Enter postgres database name: ' db_name

read -p 'Enter path to data directory: ' data_path

export POSTGRES_USER=$username
export POSTGRES_PASSWORD=$password
export DB_NAME=$db_name
export DATA_PATH=$data_path

python download_nc_voterfile.py
python download_mggg.py
python unzip_shapefiles.py
python generate_db_raw.py
