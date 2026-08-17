import pandas as pd
#import logging

#from os import listdir
from prestaging.prestaging_extractor import raw_files_to_df
#from prestaging.prestaging_config import DOWNLOAD_DIR

#file_dirs: list = listdir(DOWNLOAD_DIR)

#extracted_dfs: dict = {dir : raw_files_to_df(dir) for dir in file_dirs}

#for key in extracted_dfs.keys():
#    print(key)

#print(file_dirs)

dataframes, summary = raw_files_to_df("RWY")
print(summary)
