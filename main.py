import pandas as pd
import logging

from os import listdir
from raw_to_bronze.bronze_loader import raw_files_to_df
from raw_to_bronze.bronze_config import DOWNLOAD_DIR

#file_dirs: list = listdir(DOWNLOAD_DIR)

#extracted_dfs: dict = {dir : raw_files_to_df(dir) for dir in file_dirs}

#for key in extracted_dfs.keys():
#    print(key)

#print(file_dirs)

dataframes, summary = raw_files_to_df("RHU")
print(summary)

