import pandas as pd
from os import listdir
from os.path import isfile, join
from re import search

def raw_files_to_df(dir_name: str) -> dict[str,list]:
    """
    Goes through a directory and converts all xlsx or csv files to pandas DataFrames
    Args: 
        dir_name (str) the name of the directory to be searched
    
    Returns:
        dict(str, list): key is name of the searched directory, value is list of dataframes
    """

    #Note to self, this is probably going to need additional params to allow for thinks like skipping lines
    #And/or dealing with merged cells
    #Add logging for each file

    raw_dir: str = "/home/john/projects/spend_over_25/downloaded_data/"
    full_dir: str = raw_dir+dir_name

    if dir_name not in {d for d in listdir(raw_dir)}:
        raise ValueError(f"Value error: {dir_name} not found in raw data directory")
    else:
        file_list: list = [f for f in listdir(full_dir) if isfile(join(full_dir, f))]
        xlsx_list: list = [pd.read_excel(join(full_dir,f)) for f in file_list if search(r"\.xlsx$",f)]
        csv_list: list = [pd.read_csv(join(full_dir,f)) for f in file_list if search(r"\.csv$",f)]
        df_list: list = xlsx_list+csv_list
        return {(f"df_list-,{dir_name}"): df_list}